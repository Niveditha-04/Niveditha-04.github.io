import os
import re

import chromadb
from groq import Groq

EMBED_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL    = "llama-3.3-70b-versatile"
VISION_MODEL  = "meta-llama/llama-4-scout-17b-16e-instruct"
COLLECTION    = "portfolio_chunks"
CHROMA_PATH   = os.path.join(os.path.dirname(__file__), "chroma_db")

_embedder   = None
_chroma     = None
_collection = None
_groq       = None


def get_embedder():
    global _embedder
    if _embedder is None:
        print("Loading fastembed model…")
        from fastembed import TextEmbedding
        _embedder = TextEmbedding(model_name=EMBED_MODEL)
    return _embedder


def get_collection():
    global _chroma, _collection
    if _collection is None:
        _chroma     = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _chroma.get_or_create_collection(
            name     = COLLECTION,
            metadata = {"hnsw:space": "cosine"},
        )
    return _collection


def get_groq():
    global _groq
    if _groq is None:
        _groq = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq


# ── Store ──────────────────────────────────────────────────────────────────────

def embed_and_store(chunks: list[dict]):
    col      = get_collection()
    embedder = get_embedder()

    existing = col.get()
    if existing["ids"]:
        col.delete(ids=existing["ids"])

    if not chunks:
        print("No chunks to store.")
        return

    texts     = [c["text"] for c in chunks]
    ids       = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source":       c.get("source", ""),
            "title":        c.get("title", ""),
            "section_name": c.get("section_name", ""),
            "content_type": c.get("content_type", "general"),
        }
        for c in chunks
    ]

    print(f"Embedding {len(chunks)} chunks…")
    embeddings = [e.tolist() for e in embedder.embed(texts)]

    batch = 200
    for i in range(0, len(chunks), batch):
        col.add(
            ids        = ids[i:i+batch],
            embeddings = embeddings[i:i+batch],
            documents  = texts[i:i+batch],
            metadatas  = metadatas[i:i+batch],
        )
    print(f"Stored {len(chunks)} chunks in ChromaDB.")

    # Print breakdown by content_type
    from collections import Counter
    ct = Counter(c.get("content_type", "general") for c in chunks)
    for k, v in sorted(ct.items()):
        print(f"  {k}: {v} chunks")


# ── Retrieve ───────────────────────────────────────────────────────────────────

# Maps question patterns → content_type to filter on
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


def retrieve(question: str, top_k: int = 3) -> list[str]:
    col   = get_collection()
    count = col.count()
    if count == 0:
        return []

    q_emb    = [list(get_embedder().embed([question]))[0].tolist()]
    ctype    = _detect_filter(question)
    n_result = min(top_k, count)

    # Try filtered retrieval first; fall back to unfiltered if empty
    if ctype:
        try:
            results = col.query(
                query_embeddings = q_emb,
                n_results        = n_result,
                where            = {"content_type": {"$eq": ctype}},
            )
            docs = results["documents"][0] if results["documents"] else []
            if docs:
                return docs
        except Exception:
            pass

    # Unfiltered fallback
    results = col.query(query_embeddings=q_emb, n_results=n_result)
    return results["documents"][0] if results["documents"] else []


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

    rag_chunks = retrieve(question)
    # Cap each chunk at 600 chars to keep token usage low
    rag_context = "\n\n---\n\n".join(c[:600] for c in rag_chunks) if rag_chunks else "No specific context found."

    # Prepend uploaded file text if provided
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
