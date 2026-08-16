import os
import pdfplumber
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "finance_rag")
EMBED_MODEL = "nomic-embed-text"


def extract_pages(file_obj) -> List[Tuple[str, int]]:
    """Extract text from each PDF page and keep page numbers."""
    results = []

    with pdfplumber.open(file_obj) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            results.append((text, i))

    return results


def ingest_files(uploaded_files) -> Tuple[int, int]:
    texts = []
    metadatas = []
    file_count = 0

    # Extract text from PDFs
    for up in uploaded_files:
        file_count += 1
        fname = up.name

        pages = extract_pages(up)

        for text, page in pages:
            if not text.strip():
                continue

            texts.append(text)
            metadatas.append({
                "file": fname,
                "page": page
            })

    # Convert extracted text into LangChain Documents
    documents = [
        Document(page_content=text, metadata=metadata)
        for text, metadata in zip(texts, metadatas)
    ]

    # Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    docs = splitter.split_documents(documents)

    # Ollama embeddings
    embeddings = OllamaEmbeddings(
        model=EMBED_MODEL
    )

    # Store embeddings in persistent ChromaDB
    chroma = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )

    chroma.add_documents(docs)

    return file_count, len(docs)