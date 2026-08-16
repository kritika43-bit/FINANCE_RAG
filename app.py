import os
from dotenv import load_dotenv
import streamlit as st
from ingest import ingest_files
from rag import answer_query, get_chroma_stats

load_dotenv()

st.set_page_config(page_title="Fin.", layout="wide")

st.title("Fin. RAG — Quarterly Financial Reports")

uploaded = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("Index uploaded files"):
        if not uploaded:
            st.warning("Please upload at least one PDF file.")
        else:
            files_processed, chunks = ingest_files(uploaded)
            st.success(f"{files_processed} files processed, {chunks} chunks stored")

with col2:
    stats = get_chroma_stats()
    if stats:
        st.write("**Index stats**")
        st.write(stats)

st.markdown("---")

query = st.text_input("Ask a question about the uploaded reports")
top_k = st.slider("Top K sources to retrieve", 1, 10, 4)
if st.button("Ask"):
    if not query:
        st.warning("Please enter a question.")
    else:
        answer, sources = answer_query(query, top_k=top_k, temperature=0.0)
        st.subheader("Answer")
        st.write(answer)
        st.subheader("Sources")
        for src in sources:
            st.write(f"- {src['file']} (page {src['page']}) — score: {src.get('score', '')}")
