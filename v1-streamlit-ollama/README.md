# 📚 RAG Paper Explainer — v1: Streamlit + Ollama

**Version 1 of 3** — runs entirely locally using Ollama. No API key, no cost, no data leaves your machine.

> See also: [v2 — FastAPI + HTML + Ollama](../v2-fastapi-html-ollama) · [v3 — FastAPI + Groq + AWS](../v3-fastapi-groq-aws)

---

## What It Does

Upload any research paper PDF and ask questions about it in plain English. Get precise, page-cited answers based only on what the paper actually says — not hallucinated summaries.

```
You:   "What statistical methods did they use?"
App:   "According to Page 4, the authors applied
        survival analysis and semi-supervised clustering..."
```

---

## Architecture

```
Browser (Streamlit UI)
        │
        ▼
  app.py (Streamlit)
        │
        ▼
  rag_pipeline.py
  ┌─────────────────────────────────────┐
  │ 1. Extract text    (PyMuPDF)        │
  │ 2. Chunk text      (LangChain)      │
  │ 3. Embed chunks    (sentence-       │
  │                     transformers)   │
  │ 4. Store in        (ChromaDB)       │
  │ 5. Retrieve top-5  (cosine sim)     │
  │ 6. Generate answer (Ollama)         │
  └─────────────────────────────────────┘
        │
        ▼
  Ollama (local)
  Llama 3.2 running on your Mac
```

---

## Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| PDF parsing | PyMuPDF |
| Text chunking | LangChain Text Splitters |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector database | ChromaDB (in-memory) |
| LLM | Llama 3.2 via Ollama (local) |

---

## Prerequisites

- Python 3.10+
- macOS with 8GB+ RAM recommended
- Ollama installed

---

## Setup

```bash
# Step 1: Install Ollama
brew install --cask ollama

# Open the Ollama app from Applications
# It will appear in your menu bar

# Step 2: Pull the model (first time only, ~2GB download)
ollama pull llama3.2

# Step 3: Clone / download this project
cd v1-streamlit-ollama

# Step 4: Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 5: Install dependencies
pip install -r requirements.txt

# Step 6: Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## Usage

1. Upload a PDF using the sidebar file uploader
2. Click **Load Paper** and wait ~10 seconds for indexing
3. Use the **Quick Action** buttons or type your own question
4. Every answer cites the page it came from

---

## How RAG Works

**Without RAG:** send the whole paper to the LLM every time → expensive, slow, hits context limits, can hallucinate.

**With RAG:**
1. The paper is split into small overlapping chunks (800 chars, 100 overlap)
2. Each chunk is converted into a vector embedding (numerical representation of meaning)
3. When you ask a question, your question is also embedded
4. The 5 most similar chunks are retrieved from ChromaDB
5. Only those 5 chunks + your question are sent to Llama 3.2
6. The model answers using only what's in those chunks

This means answers are **grounded in the paper**, not invented.

---

## Limitations

- **Local model quality** — Llama 3.2 (3B parameters) is good but not as capable as larger models. Answers on complex papers may be simpler than you'd like.
- **RAM requirement** — Llama 3.2 needs ~4GB RAM. On machines with less, try `ollama pull llama3.2:1b` (smaller variant).
- **In-memory only** — ChromaDB resets when you restart the app. Re-upload your PDF each session.
- **Not deployable as-is** — Ollama can't run on cloud free tiers (1GB RAM). See [v3](../v3-fastapi-groq-aws) for cloud deployment.

---

## Upgrading

- **Better answers** → pull a larger model: `ollama pull llama3.1:8b`
- **Web frontend** → see [v2](../v2-fastapi-html-ollama)
- **Deploy to cloud** → see [v3](../v3-fastapi-groq-aws)
