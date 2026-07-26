"""
main.py — FastAPI backend for RAG Paper Explainer (Ollama version)
------------------------------------------------------------------
Run locally:  uvicorn main:app --reload
Then open:    http://localhost:8000

Note: this version uses Ollama (local model).
      For cloud deployment, use v3 (Groq API).
"""

import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from rag_pipeline import PDFExplainer

app = FastAPI(title="RAG Paper Explainer — Ollama")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at the root URL
@app.get("/")
def root():
    return FileResponse("index.html")

@app.get("/health")
def health():
    return {"status": "ok", "model": "llama3.2 via Ollama (local)"}

# Single global explainer — one paper loaded at a time
explainer = PDFExplainer(model_name="llama3.2")


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Receive a PDF, index it, return confirmation."""
    contents = await file.read()
    try:
        explainer.load_pdf(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "message": f"Loaded: {explainer.paper_title}",
        "chunks": explainer.collection.count() if explainer.collection else 0
    }


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask(request: QuestionRequest):
    """Receive a question, return the answer."""
    if not explainer.collection:
        raise HTTPException(
            status_code=404,
            detail="No paper loaded. Upload a PDF first."
        )
    try:
        answer = explainer.ask(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"answer": answer}
