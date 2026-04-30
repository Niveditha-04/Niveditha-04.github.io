# Niveditha Srikanth — Portfolio

**Live site:** https://niveditha-04.github.io

---

## AI Chatbot

The portfolio has a built-in AI chatbot. It knows about me and can answer questions about my work, projects, publications, research, experience, and background, all in first person as if you are talking directly to me.

You can find the chatbot by clicking the purple button at the bottom right corner of the site.

### What you can do

- Ask anything about me 
- Send an image and ask a question about it
- Click the Listen button on any reply to hear it read out loud
- Use the mic button to speak your question instead of typing

### Things to know before you use it

**First reply takes longer:** The chatbot runs on Render's free hosting. If no one has used it in the last 15 minutes, it goes to sleep. Your very first message may take 50 seconds to 1 minute to get a reply. After that, all replies come back instantly

**Daily usage limit:** The chatbot uses the Groq API which has a free daily token limit. Each reply uses roughly 300 to 500 tokens. The daily limit covers around 150 to 200 exchanges on a normal day. If the limit is reached, the chatbot will let you know and suggest reaching out by email instead

---

## How the Chatbot Works

This is a RAG (Retrieval Augmented Generation) chatbot. Here is what happens when you ask a question:

1. The backend scrapes my portfolio and GitHub at startup and loads all the content into memory
2. When you ask something, it finds the most relevant sections from that content
3. It sends those sections along with your question to the Groq API
4. The Groq API uses Llama 3.3 70B to generate a reply in first person
5. The reply appears in the chat

For image questions, the chatbot uses the Llama 4 Scout vision model via Groq.

---

## Tech Stack

| Part | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| LLM | Groq API, Llama 3.3 70B |
| Vision | Groq API, Llama 4 Scout |
| RAG | Keyword retrieval, in-memory search |
| Scraping | BeautifulSoup4, GitHub API |
| Frontend | Vanilla JS widget embedded in portfolio |
| Hosting | Render free tier |

---

## Source Code

The full chatbot code is inside the `portfolio-chatbot/` folder in this repo.

**Backend:** [`portfolio-chatbot/backend/`](https://github.com/Niveditha-04/Niveditha-04.github.io/tree/main/portfolio-chatbot/backend)

**Frontend widget:** [`portfolio-chatbot/frontend/chatbot.html`](https://github.com/Niveditha-04/Niveditha-04.github.io/blob/main/portfolio-chatbot/frontend/chatbot.html)

**Render config:** [`portfolio-chatbot/render.yaml`](https://github.com/Niveditha-04/Niveditha-04.github.io/blob/main/portfolio-chatbot/render.yaml)

If you want to run this for your own portfolio, you will need a free Groq API key from console.groq.com and a free Render account. Set the environment variables `GROQ_API_KEY`, `GITHUB_USERNAME`, and `PORTFOLIO_URL` in your Render service, and it will scrape and learn your own content automatically.

---

## Contact

You can reach me through the email on the portfolio or connect with me on LinkedIn. The chatbot is also a good way to learn more about my work quickly
