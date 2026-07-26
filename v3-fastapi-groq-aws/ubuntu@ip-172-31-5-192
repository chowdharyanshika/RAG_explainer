"""
main.py — FastAPI backend for RAG Paper Explainer
--------------------------------------------------
Local:  uvicorn main:app --reload
EC2:    uvicorn main:app --host 0.0.0.0 --port 8000

Users pass their own Groq API key per session.
Groq is free at console.groq.com — no credit card needed.
"""

import io
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from rag_pipeline import PDFExplainer

app = FastAPI(title="RAG Paper Explainer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the HTML frontend at /
@app.get("/")
def root():
    return FileResponse("index.html")

@app.get("/health")
def health():
    return {"status": "ok", "model": "llama-3.3-70b via Groq"}

# One explainer stored per Groq API key
explainers: dict = {}


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    groq_api_key: str = Form("")
):
    if not groq_api_key:
        raise HTTPException(
            status_code=400,
            detail="Groq API key required. Get one free at console.groq.com"
        )

    contents = await file.read()

    try:
        explainer = PDFExplainer(groq_api_key=groq_api_key)
        explainer.load_pdf(io.BytesIO(contents))
        explainers[groq_api_key] = explainer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "message": f"Loaded: {explainer.paper_title}",
        "chunks": explainer.collection.count() if explainer.collection else 0
    }


class QuestionRequest(BaseModel):
    question: str
    groq_api_key: str


@app.post("/ask")
def ask(request: QuestionRequest):
    if not request.groq_api_key:
        raise HTTPException(status_code=400, detail="Groq API key required")

    explainer = explainers.get(request.groq_api_key)
    if not explainer or not explainer.collection:
        raise HTTPException(
            status_code=404,
            detail="No paper loaded. Upload a PDF first."
        )

    try:
        answer = explainer.ask(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"answer": answer}