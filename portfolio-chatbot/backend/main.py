import asyncio
import io
import os
import re
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from file_processor import extract_text
from github_fetch import fetch_github_repos, fetch_single_repo
from rag import chat as rag_chat, embed_and_store
from scraper import load_extra_info, scrape_local_html, scrape_portfolio
from voice import load_tts, synthesize

PORTFOLIO_NAME = "Niveditha Srikanth"
GH_URL_RE      = re.compile(r"https?://github\.com/[\w.\-]+/[\w.\-]+")


# ── Startup scrape ─────────────────────────────────────────────────────────────

def run_scrape():
    portfolio_url   = os.environ.get("PORTFOLIO_URL", "").strip()
    github_username = os.environ.get("GITHUB_USERNAME", "").strip()
    local_html_path = os.environ.get("LOCAL_HTML_PATH", "").strip()
    extra_path      = os.path.join(os.path.dirname(__file__), "extra_info.md")

    all_chunks: list[dict] = []

    # 1. Local HTML — always prioritised (full content, section-aware)
    if local_html_path and os.path.exists(local_html_path):
        all_chunks.extend(scrape_local_html(local_html_path))
    else:
        guessed = os.path.join(os.path.dirname(__file__), "portfolio.html")
        if os.path.exists(guessed):
            print(f"Auto-detected local HTML: {guessed}")
            all_chunks.extend(scrape_local_html(guessed))

    # 2. Live website (supplements local HTML with any dynamic content)
    if portfolio_url:
        all_chunks.extend(scrape_portfolio(portfolio_url))
    else:
        print("PORTFOLIO_URL not set — skipping live scrape.")

    # 3. GitHub repos
    if github_username:
        all_chunks.extend(fetch_github_repos(github_username))
    else:
        print("GITHUB_USERNAME not set — skipping GitHub fetch.")

    # 4. Personal extra info
    all_chunks.extend(load_extra_info(extra_path))

    print(f"\nTotal chunks to embed: {len(all_chunks)}")
    embed_and_store(all_chunks)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n========= Portfolio Chatbot Backend starting =========")
    await asyncio.to_thread(run_scrape)
    await asyncio.to_thread(load_tts)
    print("========= Ready =========\n")
    yield


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Portfolio Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)


# ── Models ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message:      str
    history:      list  = []
    image:        str | None = None   # base64 image for vision
    file_context: str | None = None   # extracted text from uploaded doc


class SpeakRequest(BaseModel):
    text: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "name": PORTFOLIO_NAME}


@app.post("/chat")
async def chat(req: ChatRequest):
    message = req.message.strip()
    if not message and not req.file_context:
        raise HTTPException(400, "Empty message")

    # Auto-fetch GitHub repo if URL pasted
    gh_match = GH_URL_RE.search(message)
    if gh_match:
        repo_data = await asyncio.to_thread(fetch_single_repo, gh_match.group(0))
        if repo_data:
            message = f"{message}\n\n[Auto-fetched GitHub repo]\n{repo_data}"

    answer = await asyncio.to_thread(
        rag_chat,
        message or "What is in this document?",
        req.history,
        PORTFOLIO_NAME,
        req.image,
        req.file_context,
    )
    return {"answer": answer}


@app.post("/extract")
async def extract_file(file: UploadFile = File(...)):
    """Extract text from PDF / DOCX / TXT / CSV and return it."""
    content = await file.read()
    text    = extract_text(file.filename or "", content)
    if not text:
        raise HTTPException(400, f"Could not extract text from '{file.filename}'")
    # Cap at 12 000 chars so we don't overflow Groq context
    return {"text": text[:12000], "filename": file.filename}


@app.post("/speak")
async def speak(req: SpeakRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Empty text")

    voice_ref = os.environ.get("VOICE_REF_PATH", "my_voice.wav")
    if not os.path.isabs(voice_ref):
        voice_ref = os.path.join(os.path.dirname(__file__), voice_ref)

    if not os.path.exists(voice_ref):
        raise HTTPException(404, f"Voice file not found: {voice_ref}. Place my_voice.wav in backend/.")

    try:
        audio_bytes = await asyncio.to_thread(synthesize, text, voice_ref)
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type = "audio/wav",
        headers    = {"Content-Disposition": "inline; filename=response.wav"},
    )


@app.post("/refresh")
async def refresh():
    await asyncio.to_thread(run_scrape)
    return {"status": "refreshed"}
