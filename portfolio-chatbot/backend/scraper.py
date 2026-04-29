import os
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

SKIP_TAGS = {"nav", "footer", "header", "script", "style", "noscript", "aside", "form"}
MAX_PAGES  = 25
CHUNK_SIZE = 350
OVERLAP    = 60

SKIP_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".mp4", ".mp3", ".wav", ".zip", ".docx", ".pptx", ".xlsx",
    ".m4a", ".mov", ".avi", ".ico",
}

# Map section IDs → content_type
SECTION_MAP = {
    "about":        "about",
    "experience":   "experience",
    "projects":     "project",
    "achievements": "achievement",
    "blog":         "blog",
    "contact":      "contact",
    "hero":         "about",
}

# Publication sub-panels → specific content_type
PUB_PANEL_MAP = {
    "pub-research":   "publication_research",
    "pub-copyrights": "publication_copyright",
    "pub-patents":    "publication_patent",
    "pub-book":       "publication_book_chapter",
}


# ── Utilities ──────────────────────────────────────────────────────────────────

def _clean_node(node) -> str:
    """Extract clean text from a BS4 node."""
    for tag in node(["script", "style", "noscript"]):
        tag.decompose()
    text  = node.get_text(separator="\n")
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l and len(l) > 20]
    return "\n".join(lines)


def chunk_text(text: str, source: str, title: str,
               section_name: str = "", content_type: str = "general") -> list[dict]:
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end   = min(start + CHUNK_SIZE, len(words))
        piece = " ".join(words[start:end])
        if len(piece.strip()) > 60:
            chunks.append({
                "text":         piece,
                "source":       source,
                "title":        title,
                "section_name": section_name,
                "content_type": content_type,
            })
        start += CHUNK_SIZE - OVERLAP
    return chunks


# ── Local HTML scraper (section-aware) ────────────────────────────────────────

def scrape_local_html(html_path: str) -> list[dict]:
    if not os.path.exists(html_path):
        print(f"Local HTML not found: {html_path}")
        return []

    print(f"\n--- Reading local HTML: {html_path} ---")
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    source = "local_portfolio"
    chunks: list[dict] = []

    # ── Publications section — split by sub-panel ──────────────────────────
    pub_section = soup.find("section", id="publications")
    if pub_section:
        for panel_id, ctype in PUB_PANEL_MAP.items():
            panel = pub_section.find(id=panel_id)
            if not panel:
                continue
            # Collect each publication card as its own chunk for precision
            cards = panel.find_all(class_="pub-card") or panel.find_all(class_=re.compile("pub"))
            if cards:
                for card in cards:
                    text = _clean_node(card)
                    if text:
                        chunks.extend(chunk_text(
                            text, source,
                            title        = f"Publication ({ctype})",
                            section_name = panel_id,
                            content_type = ctype,
                        ))
            else:
                # Fallback: whole panel text
                text = _clean_node(panel)
                if text:
                    chunks.extend(chunk_text(
                        text, source,
                        title        = f"Publication ({ctype})",
                        section_name = panel_id,
                        content_type = ctype,
                    ))
        print(f"  Publications → {sum(1 for c in chunks if 'publication' in c['content_type'])} chunks")

    # ── All other named sections ───────────────────────────────────────────
    for sec_id, ctype in SECTION_MAP.items():
        section = soup.find("section", id=sec_id)
        if not section:
            continue

        # For projects: extract each project card individually
        if ctype == "project":
            cards = section.find_all(class_=re.compile(r"project.card|proj.card|pc-card|project-card-ac", re.I))
            if cards:
                for card in cards:
                    text = _clean_node(card)
                    if text:
                        chunks.extend(chunk_text(
                            text, source,
                            title        = "Project",
                            section_name = sec_id,
                            content_type = "project",
                        ))
                print(f"  Projects → {sum(1 for c in chunks if c['content_type']=='project')} chunks")
                continue

        # For experience: extract each timeline item individually
        if ctype == "experience":
            items = section.find_all(class_=re.compile(r"tl-item|timeline.item|exp.item|exp-card", re.I))
            if not items:
                items = section.find_all(class_=re.compile(r"card|entry|role|job", re.I))
            if items:
                for item in items:
                    text = _clean_node(item)
                    if text:
                        chunks.extend(chunk_text(
                            text, source,
                            title        = "Experience",
                            section_name = sec_id,
                            content_type = "experience",
                        ))
                print(f"  Experience → {sum(1 for c in chunks if c['content_type']=='experience')} chunks")
                continue

        # For blog: extract each blog card individually
        if ctype == "blog":
            cards = section.find_all(class_=re.compile(r"blog.card|blog-card|post.card|article", re.I))
            if cards:
                for card in cards:
                    text = _clean_node(card)
                    if text:
                        chunks.extend(chunk_text(
                            text, source,
                            title        = "Blog Post",
                            section_name = sec_id,
                            content_type = "blog",
                        ))
                print(f"  Blog → {sum(1 for c in chunks if c['content_type']=='blog')} chunks")
                continue

        # Default: chunk the whole section
        text = _clean_node(section)
        if text:
            n_before = len(chunks)
            chunks.extend(chunk_text(
                text, source,
                title        = sec_id.capitalize(),
                section_name = sec_id,
                content_type = ctype,
            ))
            print(f"  {sec_id} → {len(chunks)-n_before} chunks")

    print(f"Total from local HTML: {len(chunks)} chunks")
    return chunks


# ── Network scraper (fallback / supplemental) ──────────────────────────────────

def _fetch(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (portfolio-chatbot)"}
    r = requests.get(url, headers=headers, timeout=12)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def _links(base: str, soup: BeautifulSoup):
    domain = urlparse(base).netloc
    seen   = set()
    for a in soup.find_all("a", href=True):
        href   = urljoin(base, a["href"])
        parsed = urlparse(href)
        if parsed.netloc == domain and parsed.scheme in ("http", "https"):
            clean = href.split("#")[0].rstrip("/")
            ext   = os.path.splitext(parsed.path)[1].lower()
            if clean and clean not in seen and ext not in SKIP_EXTENSIONS:
                seen.add(clean)
                yield clean


def scrape_portfolio(portfolio_url: str) -> list[dict]:
    root    = portfolio_url.rstrip("/")
    visited = set()
    queue   = [root]
    all_chunks: list[dict] = []

    print(f"\n--- Scraping live site: {root} ---")
    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext in SKIP_EXTENSIONS:
            continue
        try:
            print(f"  GET {url}")
            soup  = _fetch(url)
            title = (soup.title.string if soup.title and soup.title.string else url).strip()
            for tag in soup(SKIP_TAGS):
                tag.decompose()
            text  = soup.get_text(separator="\n")
            lines = [l.strip() for l in text.splitlines() if l.strip() and len(l.strip()) > 25]
            text  = "\n".join(lines)
            if text:
                all_chunks.extend(chunk_text(text, url, title, section_name="live_page", content_type="general"))
            for link in _links(root, soup):
                if link not in visited:
                    queue.append(link)
        except Exception as e:
            print(f"  ✗ {url}: {e}")
        time.sleep(0.25)

    print(f"Live scrape: {len(visited)} pages → {len(all_chunks)} chunks")
    return all_chunks


# ── Extra info loader ──────────────────────────────────────────────────────────

def load_extra_info(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        print(f"Loaded extra_info.md ({len(text)} chars)")
        return chunk_text(text, "extra_info.md", "Personal Information",
                          section_name="personal", content_type="personal")
    except FileNotFoundError:
        print("extra_info.md not found — skipping.")
        return []
