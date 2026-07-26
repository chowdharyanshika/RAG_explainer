"""
RAG Pipeline — Groq version (deployable on AWS EC2 free tier)
--------------------------------------------------------------
Swaps Ollama (needs 4GB RAM) for Groq API (free, fast, no GPU needed).

Why Groq:
  → Free: 1,000 requests/day, no credit card
  → Runs Llama 3.3 70B — much better than local llama3.2
  → OpenAI-compatible API format
  → Works on t2.micro (1GB RAM) — no local model needed
  → Sign up: console.groq.com
"""

import io
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq


class PDFExplainer:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"

        # ChromaDB in memory — no server needed
        self.chroma_client = chromadb.Client()

        # Sentence transformers for embeddings — lightweight, ~90MB
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = None
        self.paper_title = "the paper"

    def load_pdf(self, uploaded_file) -> None:
        """Extract text, chunk, embed, store in ChromaDB."""

        # Handle BytesIO (FastAPI) or Streamlit UploadedFile
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

        # Fresh collection per paper
        try:
            self.chroma_client.delete_collection("paper")
        except Exception:
            pass

        self.collection = self.chroma_client.create_collection(
            name="paper",
            embedding_function=self.embedding_fn
        )

        # Batch insert
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            self.collection.add(
                documents=chunks[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
                ids=ids[i:i + batch_size]
            )

        print(f"Indexed {len(chunks)} chunks from {len(pages)} pages.")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Find most relevant chunks for a query."""
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
        """RAG: retrieve relevant chunks, send to Groq, return answer."""
        chunks = self.retrieve(question, top_k=5)

        context = "\n\n---\n\n".join(
            f"[Page {c['page']}]\n{c['text']}" for c in chunks
        )

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f'You are a helpful research assistant explaining academic papers. '
                        f'You are answering questions about: "{self.paper_title}". '
                        f'Base your answers ONLY on the provided context. '
                        f'If the context does not contain enough information, say so honestly. '
                        f'Always mention which page(s) your answer comes from.'
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Context from the paper:\n\n{context}\n\n"
                        f"---\n\nQuestion: {question}\n\n"
                        f"Answer based only on the context above and cite page numbers."
                    )
                }
            ]
        )

        return response.choices[0].message.content
