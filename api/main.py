from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from ingest import ingest_files
from rag import answer_query, get_chroma_stats

app = FastAPI()


@app.post("/ingest")
async def ingest_endpoint(files: List[UploadFile] = File(...)):
    processed, chunks = ingest_files(files)
    return {"files": processed, "chunks": chunks}


@app.post("/ask")
async def ask_endpoint(payload: dict):
    question = payload.get("question")
    top_k = payload.get("top_k", 4)
    answer, sources = answer_query(question, top_k=top_k)
    return {"answer": answer, "sources": sources}


@app.get("/stats")
async def stats():
    stats = get_chroma_stats()
    return stats or JSONResponse(status_code=404, content={"detail": "No index available"})


# To run the app use an ASGI server such as uvicorn externally:
# uvicorn api.main:app --reload
