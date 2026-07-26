# 📚 RAG Paper Explainer — v2: FastAPI + HTML + Ollama

**Version 2 of 3** — replaces the Streamlit UI with a custom HTML/CSS/JS frontend and a FastAPI backend, while keeping Ollama as the local LLM.

> See also: [v1 — Streamlit + Ollama](../v1-streamlit-ollama) · [v3 — FastAPI + Groq + AWS](../v3-fastapi-groq-aws)

---

## What Changed from v1

| | v1 Streamlit | v2 FastAPI + HTML |
|---|---|---|
| Frontend | Streamlit components | Custom HTML/CSS/JS |
| Backend | Streamlit server | FastAPI REST API |
| UI flexibility | Limited | Full control |
| API access | No | Yes — `/upload` and `/ask` |
| Deployable | Local only | Local only (Ollama constraint) |
| LLM | Ollama (local) | Ollama (local) |

The main reason to move from Streamlit to FastAPI + HTML is **control**: you own the entire frontend, can style it however you want, and expose proper REST endpoints that other services could call.

---

## Architecture

```
Browser (index.html)
   │  fetch() API calls
   ▼
FastAPI backend (main.py)
   ├── GET  /          → serves index.html
   ├── GET  /health    → health check
   ├── POST /upload    → index a PDF
   └── POST /ask       → answer a question
         │
         ▼
   rag_pipeline.py
   (same as v1 — PDF → chunks → embeddings → ChromaDB → Ollama)
         │
         ▼
   Ollama (local)
   Llama 3.2 on your Mac
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend | Vanilla HTML / CSS / JS |
| PDF parsing | PyMuPDF |
| Text chunking | LangChain Text Splitters |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector database | ChromaDB (in-memory) |
| LLM | Llama 3.2 via Ollama (local) |

---

## Project Structure

```
v2-fastapi-html-ollama/
├── main.py           # FastAPI backend — REST API endpoints
├── rag_pipeline.py   # RAG logic (identical to v1)
├── index.html        # Custom HTML/CSS/JS frontend
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Ollama installed and running with llama3.2 pulled

```bash
# Install Ollama
brew install --cask ollama

# Pull model (first time only)
ollama pull llama3.2
```

---

## Setup & Run

```bash
cd v2-fastapi-html-ollama

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make sure Ollama is running (open the app or:)
ollama serve

# Start the FastAPI server
uvicorn main:app --reload
```

Open **http://localhost:8000** — the HTML frontend loads automatically.

---

## API Reference

### `POST /upload`

Upload and index a PDF file.

**Form data:** `file` (PDF)

**Response:**
```json
{
  "status": "ok",
  "message": "Loaded: Paper Title Here",
  "chunks": 142
}
```

### `POST /ask`

Ask a question about the loaded paper.

**Request:**
```json
{"question": "What methods did the authors use?"}
```

**Response:**
```json
{"answer": "According to Page 4, the authors used..."}
```

### `GET /health`

```json
{"status": "ok", "model": "llama3.2 via Ollama (local)"}
```

---

## Why FastAPI over Streamlit?

1. **REST API** — `/ask` can be called by any client (mobile app, another service, curl)
2. **Custom UI** — full control over design, layout, animations
3. **Production pattern** — separating frontend from backend is standard in industry
4. **Testable** — FastAPI auto-generates interactive docs at `/docs`

---

## Limitations

- **Ollama not cloud-deployable on free tier** — t2.micro (1GB RAM) can't run Llama 3.2 (needs ~4GB). For cloud deployment, see [v3](../v3-fastapi-groq-aws).
- **Single paper** — one paper loaded globally. Multiple users would overwrite each other's paper.
- **In-memory** — ChromaDB resets on server restart.

---

## Upgrading

- **Deploy to cloud** → see [v3](../v3-fastapi-groq-aws) — swaps Ollama for Groq and deploys to AWS EC2
