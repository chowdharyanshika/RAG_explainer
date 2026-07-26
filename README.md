# 📚 RAG Paper Explainer — Three Versions

A Retrieval-Augmented Generation (RAG) system that lets you upload any academic PDF and ask questions about it in plain English. Built in three progressive versions, each adding production capability.

---

## The Three Versions

| | v1 | v2 | v3 |
|---|---|---|---|
| **Frontend** | Streamlit | Custom HTML/CSS/JS | Custom HTML/CSS/JS |
| **Backend** | Streamlit | FastAPI | FastAPI |
| **LLM** | Ollama (local) | Ollama (local) | Groq API (cloud, free) |
| **Model** | Llama 3.2 (3B) | Llama 3.2 (3B) | Llama 3.3 70B |
| **Deployable to cloud** | ❌ | ❌ | ✅ |
| **RAM needed** | 4GB+ | 4GB+ | 1GB (EC2 free tier) |
| **API key needed** | None | None | Groq (free) |
| **Best for** | Local dev | Local dev + API | Portfolio / production |

---

## Which Version to Use

```
Just want to run it locally and test?
→ Start with v1 (simplest setup)

Want to see the FastAPI + HTML pattern?
→ Use v2 (same local setup, better architecture)

Want a live public URL on AWS for your portfolio?
→ Use v3 (Groq API + EC2 deployment)
```

---

## Shared Architecture (all versions)

All three versions use the same RAG pipeline:

```
PDF Upload
    │
    ▼
PyMuPDF         → extract text page by page
    │
    ▼
LangChain        → split into 800-char chunks (100 overlap)
    │
    ▼
sentence-transformers → embed each chunk (all-MiniLM-L6-v2)
    │
    ▼
ChromaDB         → store embeddings in memory
    │
    ▼         ← at query time
User question → embed → find top-5 similar chunks
    │
    ▼
LLM (Ollama/Groq) → generate answer grounded in chunks
    │
    ▼
Answer with page citations
```

The only thing that changes between versions is:
- **Frontend**: Streamlit (v1) vs HTML (v2, v3)
- **Backend**: Streamlit server (v1) vs FastAPI (v2, v3)
- **LLM**: Ollama local (v1, v2) vs Groq cloud API (v3)

---

## Quick Start

```bash
# V1 — Streamlit + Ollama
cd v1-streamlit-ollama
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

# V2 — FastAPI + HTML + Ollama
cd v2-fastapi-html-ollama
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# open http://localhost:8000

# V3 — FastAPI + Groq + AWS
cd v3-fastapi-groq-aws
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# open http://localhost:8000
# (needs free Groq API key from console.groq.com)
```

---

## Related Projects

- **[Autonomous Literature Review Agent](../lit-review-agent)** — give it a topic, it autonomously searches PubMed and ArXiv and writes a structured review using a ReAct loop
- **[PRS Analysis Pipeline](../prs-agent)** — end-to-end polygenic risk score pipeline (Python, Nextflow, Docker, Singularity)
- **[Customer Churn Prediction](../churn-xgboost)** — XGBoost classification pipeline with AUC 0.84
