import base64
import os
import re
import time

import requests


def _headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    return {"Authorization": f"token {token}"} if token else {}


def _strip_markdown(text: str) -> str:
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)            # images
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # links
    text = re.sub(r"#{1,6}\s*", "", text)                   # headings
    text = re.sub(r"`{1,3}[^`]*`{1,3}", "", text, flags=re.S)  # code
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_readme(username: str, repo: str) -> str:
    try:
        url  = f"https://api.github.com/repos/{username}/{repo}/readme"
        r    = requests.get(url, headers=_headers(), timeout=10)
        if r.status_code != 200:
            return ""
        raw  = base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
        return _strip_markdown(raw)[:2000]
    except Exception:
        return ""


def fetch_github_repos(username: str) -> list[dict]:
    chunks = []
    page   = 1

    print(f"\n--- Fetching GitHub repos for @{username} ---")
    while True:
        try:
            r = requests.get(
                f"https://api.github.com/users/{username}/repos",
                headers = _headers(),
                params  = {"per_page": 50, "page": page, "type": "public", "sort": "updated"},
                timeout = 12,
            )
            r.raise_for_status()
            repos = r.json()
        except Exception as e:
            print(f"  GitHub API error: {e}")
            break

        if not repos:
            break

        for repo in repos:
            name  = repo["name"]
            parts = [
                f"GitHub Repository: {name}",
                f"Description: {repo.get('description') or 'No description provided'}",
                f"Primary language: {repo.get('language') or 'not specified'}",
                f"Topics: {', '.join(repo.get('topics', [])) or 'none'}",
                f"Stars: {repo.get('stargazers_count', 0)}",
                f"URL: {repo.get('html_url', '')}",
            ]
            readme = fetch_readme(username, name)
            if readme:
                parts.append(f"README:\n{readme}")

            chunks.append({
                "text":   "\n".join(parts),
                "source": repo.get("html_url", ""),
                "title":  f"GitHub: {name}",
            })
            time.sleep(0.08)

        page += 1
        if len(repos) < 50:
            break

    print(f"Fetched {len(chunks)} repos from GitHub")
    return chunks


def fetch_single_repo(url: str) -> str:
    """Fetch metadata + README for one specific GitHub repo URL."""
    try:
        parts    = url.rstrip("/").split("/")
        username = parts[-2]
        repo     = parts[-1]
        r        = requests.get(
            f"https://api.github.com/repos/{username}/{repo}",
            headers = _headers(),
            timeout = 10,
        )
        data = r.json()
        info = [
            f"Repository: {data.get('name', repo)}",
            f"Description: {data.get('description') or 'No description'}",
            f"Language: {data.get('language') or 'not specified'}",
            f"Topics: {', '.join(data.get('topics', []))}",
            f"Stars: {data.get('stargazers_count', 0)}",
        ]
        readme = fetch_readme(username, repo)
        if readme:
            info.append(f"README:\n{readme}")
        return "\n".join(info)
    except Exception as e:
        print(f"fetch_single_repo error: {e}")
        return ""
