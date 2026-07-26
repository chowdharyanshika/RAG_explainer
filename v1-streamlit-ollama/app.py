"""
app.py — Streamlit frontend for RAG Paper Explainer (Ollama version)
---------------------------------------------------------------------
Run with: streamlit run app.py
"""

import streamlit as st
from rag_pipeline import PDFExplainer

st.set_page_config(
    page_title="Research Paper Explainer",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Research Paper Explainer")
st.caption("Upload a paper, ask questions, get plain-English answers — powered by Llama 3.2 running locally.")

# ── Session state ────────────────────────────────────────────────
if "explainer" not in st.session_state:
    st.session_state.explainer = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "paper_loaded" not in st.session_state:
    st.session_state.paper_loaded = False

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Setup")
    st.info(
        "🦙 Using Llama 3.2 via Ollama — running locally, "
        "no API key needed.\n\n"
        "Make sure Ollama is running before loading a paper."
    )

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        if st.button("📥 Load Paper", use_container_width=True):
            with st.spinner("Reading and indexing paper..."):
                try:
                    explainer = PDFExplainer(model_name="llama3.2")
                    explainer.load_pdf(uploaded_file)
                    st.session_state.explainer = explainer
                    st.session_state.paper_loaded = True
                    st.session_state.chat_history = []
                    st.success("Paper loaded! Start asking questions.")
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info(
                        "Make sure Ollama is running: "
                        "open the Ollama app or run 'ollama serve'"
                    )

    if st.session_state.paper_loaded:
        st.divider()
        st.header("🚀 Quick Actions")

        if st.button("📋 Summarise Paper", use_container_width=True):
            with st.spinner("Summarising..."):
                answer = st.session_state.explainer.ask(
                    "Give me a concise summary: what problem it solves, "
                    "methods used, key findings, and conclusions."
                )
                st.session_state.chat_history.append(
                    {"role": "user", "content": "📋 Summarise the paper"}
                )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )
                st.rerun()

        if st.button("🧒 Explain Like I'm 5", use_container_width=True):
            with st.spinner("Simplifying..."):
                answer = st.session_state.explainer.ask(
                    "Explain the main idea as simply as possible, "
                    "like explaining to a 10-year-old. Use analogies."
                )
                st.session_state.chat_history.append(
                    {"role": "user", "content": "🧒 Explain like I'm 5"}
                )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )
                st.rerun()

        if st.button("🔬 Key Methods & Results", use_container_width=True):
            with st.spinner("Extracting..."):
                answer = st.session_state.explainer.ask(
                    "What are the key methods, datasets, and experimental "
                    "results? Be specific and structured."
                )
                st.session_state.chat_history.append(
                    {"role": "user", "content": "🔬 Key Methods & Results"}
                )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )
                st.rerun()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ── Main area ────────────────────────────────────────────────────
if not st.session_state.paper_loaded:
    st.info("👈 Upload a PDF to get started.")
    with st.expander("Prerequisites"):
        st.markdown("""
        1. Install Ollama: `brew install --cask ollama`
        2. Open the Ollama app from Applications
        3. Pull the model (first time only): `ollama pull llama3.2`
        4. Come back here and upload your PDF
        """)
    with st.expander("What can this app do?"):
        st.markdown("""
        - **Summarise** any research paper in plain English
        - **Answer questions** about the paper's content
        - **ELI5 mode** — simplify complex concepts
        - **Extract methods & results** in a structured way
        - Cites **which page** each answer comes from
        - **100% local** — no API key, no cost, no data sent anywhere
        """)
else:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("Ask anything about the paper..."):
        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = st.session_state.explainer.ask(question)
            st.markdown(answer)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )
