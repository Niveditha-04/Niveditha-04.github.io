# Portfolio AI Chatbot

RAG-powered chatbot using Groq + sentence-transformers + ChromaDB + Coqui XTTS-v2.

---

## 1. Install dependencies into your existing Python venv

```bash
# Activate your venv first
source /path/to/your/venv/bin/activate

# Install everything
pip install fastapi "uvicorn[standard]" python-dotenv requests \
  beautifulsoup4 sentence-transformers chromadb groq numpy pydantic

# TTS should already be installed — verify with:
python -c "from TTS.api import TTS; print('TTS OK')"

# If not installed:
pip install TTS
```

---

## 2. Set up the .env file

The `.env` file is already created at `portfolio-chatbot/.env`.
Open it and confirm or update these values:

```
GROQ_API_KEY=your_key
GITHUB_USERNAME=Niveditha-04
PORTFOLIO_URL=https://yourportfolio.com   ← put your real URL here
VOICE_REF_PATH=my_voice.wav
```

Copy `my_voice.wav` into `portfolio-chatbot/backend/` — this is the voice reference for XTTS.

---

## 3. Run the backend

```bash
cd portfolio-chatbot/backend
source /path/to/your/venv/bin/activate
uvicorn main:app --reload --port 8000
```

On first start it will:
- Scrape your portfolio website
- Fetch all your GitHub repos + READMEs
- Load extra_info.md
- Embed everything into ChromaDB (takes 1-3 min)
- Load XTTS-v2 model (takes 30-60 sec, one-time download ~2 GB)

Subsequent starts reuse the model but re-scrape fresh every time.

---

## 4. Test everything

**Health check:**
```bash
curl http://localhost:8000/health
```

**Test chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "tell me about yourself", "history": []}'
```

**Test voice:**
```bash
curl -X POST http://localhost:8000/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey, I am Niveditha and this is my voice."}' \
  --output test_voice.wav

# Play the file
afplay test_voice.wav
```

**Test full widget:**
Open `portfolio-chatbot/frontend/chatbot.html` directly in Chrome.
The chatbot floats bottom-right. Type a question or click the mic button.

---

## 5. What to add to extra_info.md

Already pre-filled with your personal info. You can add more like:

```markdown
## Salary Expectations
I am open to discussing based on the role and company.

## Availability
I am available to start immediately / in two weeks.

## Preferred Work Style
I prefer hybrid or remote but open to in-office.

## Fun Facts
Add anything a recruiter or visitor might ask in a casual conversation.
```

Keep the tone casual — these answers go directly into the AI's context.

---

## 6. Embed the chatbot into your portfolio site

Add these two lines right before `</body>` in your `index.html`:

```html
<!-- AI Chatbot Widget -->
<script>
  // Load chatbot widget
  fetch('chatbot-widget.html')
    .then(r => r.text())
    .then(html => {
      const div = document.createElement('div');
      div.innerHTML = html;
      document.body.appendChild(div.querySelector('#cb-launcher'));
      document.body.appendChild(div.querySelector('#cb-window'));
      // Inject styles
      const style = div.querySelector('style');
      if (style) document.head.appendChild(style);
      // Inject script
      const script = document.createElement('script');
      script.textContent = div.querySelector('script').textContent;
      document.body.appendChild(script);
    });
</script>
```

**Simpler option** — just paste the entire contents of `chatbot.html`
(the `<style>` block, the two `<div>` elements, and the `<script>` block)
directly into your `index.html` before `</body>`. No iframe, no external files.

---

## Endpoints

| Method | Path       | Description                        |
|--------|------------|------------------------------------|
| GET    | /health    | Check if backend is alive          |
| POST   | /chat      | Send message, get AI answer        |
| POST   | /speak     | Text → WAV stream in your voice    |
| POST   | /refresh   | Re-scrape and re-embed everything  |

---

## File structure

```
portfolio-chatbot/
├── backend/
│   ├── main.py          ← FastAPI app, endpoints, startup scrape
│   ├── rag.py           ← ChromaDB + sentence-transformers + Groq
│   ├── scraper.py       ← BeautifulSoup website scraper + chunker
│   ├── github_fetch.py  ← GitHub API repo + README fetcher
│   ├── voice.py         ← XTTS-v2 synthesis
│   ├── extra_info.md    ← Your personal info (edit freely)
│   ├── my_voice.wav     ← Your voice reference (copy here)
│   └── requirements.txt
├── frontend/
│   └── chatbot.html     ← Standalone embeddable widget
├── .env                 ← Your secrets (never commit this)
├── .env.template        ← Safe template to share
└── README.md
```
