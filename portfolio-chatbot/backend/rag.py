import os
import re
from collections import Counter

GROQ_MODEL   = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

_chunks: list[dict] = []
_groq = None


def get_groq():
    global _groq
    if _groq is None:
        from groq import Groq
        _groq = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq


# ── Store ──────────────────────────────────────────────────────────────────────

def embed_and_store(chunks: list[dict]):
    global _chunks
    _chunks = chunks
    ct = Counter(c.get("content_type", "general") for c in chunks)
    print(f"Stored {len(chunks)} chunks in memory.")
    for k, v in sorted(ct.items()):
        print(f"  {k}: {v} chunks")


# ── Retrieve ───────────────────────────────────────────────────────────────────

_FILTER_RULES: list[tuple[str, str]] = [
    (r"\bcopyright\b",                                      "publication_copyright"),
    (r"\bpatent\b",                                         "publication_patent"),
    (r"\bbook.?chapter\b",                                  "publication_book_chapter"),
    (r"\bblog\b",                                           "blog"),
    (r"\bpublication\b|\bpaper\b|\bieee\b|\bspringer\b",    "publication_research"),
    (r"\bproject\b|\bbuilt\b|\bbuild\b",                    "project"),
    (r"\bexperience\b|\bwork(ed)?\b|\bjob\b|\bemployment\b","experience"),
    (r"\baward\b|\bachiev\b|\bcertif\b|\bhonour\b",         "achievement"),
]


def _detect_filter(question: str) -> str | None:
    q = question.lower()
    for pattern, ctype in _FILTER_RULES:
        if re.search(pattern, q):
            return ctype
    return None


def _score(text: str, words: list[str]) -> int:
    t = text.lower()
    return sum(t.count(w) for w in words)


def retrieve(question: str, top_k: int = 3) -> list[str]:
    if not _chunks:
        return []

    words = [w for w in re.findall(r'\w+', question.lower()) if len(w) > 2]
    ctype = _detect_filter(question)

    pool = [c for c in _chunks if c.get("content_type") == ctype] if ctype else _chunks
    if not pool:
        pool = _chunks

    ranked = sorted(pool, key=lambda c: _score(c["text"], words), reverse=True)
    return [c["text"][:600] for c in ranked[:top_k]]


# ── Chat ───────────────────────────────────────────────────────────────────────

def _system_prompt(name: str) -> str:
    return (
        f"You are {name}. Answer every question in first person like you are directly "
        "talking to someone in a conversation or interview. Use simple, casual, everyday words. "
        "No em dashes anywhere. No hyphens used as dashes. No bullet points unless they "
        "specifically ask for a list. No advanced vocabulary. No stiff AI phrasing. Speak in "
        "a natural flow like a real person talking. Keep answers concise and clear. If something "
        "is not in your knowledge base, say something casual like honestly I am not too sure about "
        "that one, still in your voice, never robotic. Never say you are an AI. You are this person "
        "answering questions about yourself."
    )


def chat(question: str, history: list, name: str,
         image_b64: str | None = None,
         file_context: str | None = None) -> str:

    rag_chunks  = retrieve(question)
    rag_context = "\n\n---\n\n".join(rag_chunks) if rag_chunks else "No specific context found."

    if file_context:
        context = (
            f"[Uploaded document]\n{file_context[:3000]}"
            f"\n\n---\n\n[Portfolio knowledge]\n{rag_context}"
        )
    else:
        context = rag_context

    messages = [{"role": "system", "content": _system_prompt(name)}]
    for turn in history[-4:]:
        messages.append({"role": turn["role"], "content": turn["content"]})

    user_text = f"Context from my portfolio and knowledge base:\n{context}\n\nQuestion: {question}"

    if image_b64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text",      "text": user_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        })
        model = VISION_MODEL
    else:
        messages.append({"role": "user", "content": user_text})
        model = GROQ_MODEL

    try:
        resp = get_groq().chat.completions.create(
            model       = model,
            messages    = messages,
            max_tokens  = 400,
            temperature = 0.72,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        err = str(e)
        if "rate_limit" in err or "429" in err or "Rate limit" in err:
            return "honestly I hit my daily message limit for today. the free tier resets every 24 hours so try again tomorrow, or just reach out to me directly by email!"
        if "invalid_api_key" in err or "401" in err:
            return "there seems to be an issue with my API key. let Niveditha know so she can fix it."
        return "something went wrong on my end. give it another try in a moment."
