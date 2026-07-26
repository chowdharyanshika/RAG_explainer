"""
RAG Pipeline — Streamlit + Ollama version
------------------------------------------
Runs entirely locally. No API key, no cost.
Requires Ollama running with llama3.2 pulled.

    ollama serve
    ollama pull llama3.2
    streamlit run app.py
"""

import io
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama


class PDFExplainer:
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

        # ChromaDB in memory — no server needed
        self.chroma_client = chromadb.Client()

        # Lightweight local embedding model (~90MB, downloads once)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = None
        self.paper_title = "the paper"

    def load_pdf(self, uploaded_file) -> None:
        """Extract text from PDF, chunk it, embed it, store in ChromaDB."""

        # Handle both Streamlit UploadedFile and BytesIO
        if isinstance(uploaded_file, bytes):
            pdf_bytes = uploaded_file
        elif isinstance(uploaded_file, io.BytesIO):
            pdf_bytes = uploaded_file.read()
        else:
            pdf_bytes = uploaded_file.read()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        pages = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"text": text, "page": page_num})

        if pages:
            first_lines = pages[0]["text"].split("\n")[:3]
            self.paper_title = " ".join(first_lines).strip()[:80]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " "]
        )

        chunks, metadatas, ids = [], [], []
        for page_data in pages:
            for i, chunk in enumerate(splitter.split_text(page_data["text"])):
                chunk_id = f"page{page_data['page']}_chunk{i}"
                chunks.append(chunk)
                metadatas.append({"page": page_data["page"], "source": chunk_id})
                ids.append(chunk_id)

        try:
            self.chroma_client.delete_collection("paper")
        except Exception:
            pass

        self.collection = self.chroma_client.create_collection(
            name="paper",
            embedding_function=self.embedding_fn
        )

        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            self.collection.add(
                documents=chunks[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
                ids=ids[i:i + batch_size]
            )

        print(f"Indexed {len(chunks)} chunks from {len(pages)} pages.")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Find the most relevant chunks for a given query."""
        if not self.collection:
            raise ValueError("No paper loaded. Call load_pdf() first.")

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count())
        )

        return [
            {"text": doc, "page": meta["page"]}
            for doc, meta in zip(
                results["documents"][0],
                results["metadatas"][0]
            )
        ]

    def ask(self, question: str) -> str:
        """RAG: retrieve relevant chunks, send to Ollama, return answer."""
        chunks = self.retrieve(question, top_k=5)

        context = "\n\n---\n\n".join(
            f"[Page {c['page']}]\n{c['text']}" for c in chunks
        )

        prompt = f"""You are a helpful research assistant explaining academic papers clearly.
You are answering questions about: "{self.paper_title}"

Rules:
- Base your answers ONLY on the context below
- If the context does not contain enough information, say so honestly
- Always cite which page(s) your answer comes from
- Be clear and concise

Context from the paper:
{context}

---
Question: {question}

Answer (cite page numbers):"""

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]
