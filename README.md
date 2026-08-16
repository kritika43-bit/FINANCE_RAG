# Finance RAG — Quarterly Financial Reports

This project builds a local retrieval-augmented generation (RAG) workflow for quarterly financial documents using Python, LangChain, ChromaDB, Ollama, and Streamlit.

## Project structure

- [app.py](app.py) — Streamlit interface for upload, indexing, and Q&A
- [ingest.py](ingest.py) — extracts text from PDFs, chunks it, embeds it, and stores it in Chroma
- [rag.py](rag.py) — retrieves relevant chunks and queries the local Ollama LLM
- [api/main.py](api/main.py) — optional FastAPI backend
- [requirements.txt](requirements.txt) — project dependencies
- [.env.example](.env.example) — example environment variables
- [run_smoke.py](run_smoke.py) — lightweight PDF sanity check for page and chunk counts

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure Ollama is installed and the required models are available locally:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

4. Start the app:

```bash
streamlit run app.py
```

## Configuration

The app uses these defaults:

- Chroma persistence directory: `chroma_db/`
- Chroma collection: `finance_rag`
- Embedding model: `nomic-embed-text`
- LLM model: `llama3.2:3b`

You can override the collection and model with environment variables if needed:

```env
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION_NAME=finance_rag
LLM_MODEL=llama3.2:3b
```

## Important fix

The indexing and retrieval paths must use the same Chroma collection name. The original issue was that ingestion wrote to one collection while the query path read the default empty collection; this prevented any document retrieval. The project now explicitly uses the same collection for both writing and reading.

## Chunking behavior

The PDF text is split using a recursive character splitter with:

- chunk size: 1000
- overlap: 150

This is enough to preserve context across page boundaries while keeping each chunk manageable for embedding and retrieval.

## Retrieval behavior

The app does the following:

1. Extracts page text from each uploaded PDF
2. Splits the text into chunks
3. Embeds the chunks with Ollama embeddings
4. Stores the vectors in ChromaDB
5. Retrieves the top relevant chunks for a question
6. Sends the question plus retrieved context to the local Ollama LLM
7. Refuses to answer if the documents do not contain the required information

## Example questions

1. What was total revenue in the most recent quarter you loaded?
2. Compare net profit across all the quarters you loaded. Which was highest?
3. How did revenue in the latest quarter compare with the same quarter of the previous year?
4. What did management say about the demand outlook or business environment?
5. Which business segment or geography grew fastest, and by how much?
6. What was the operating margin in each quarter, and is the trend rising or falling?
7. Was any dividend declared? State the amount per share and the record date.
8. What risks, headwinds, or challenges are mentioned in the documents?
9. Give me a three-line summary of the latest quarter for a client email.
10. Deliberate trap: "What is the CEO's personal shareholding in 2015?" — the app should reply that the information is not available.

## Validation

The project was verified with the current local Ollama setup. A live retrieval check with a real question returned a document-grounded answer, confirming that chunking and retrieval are functioning.
