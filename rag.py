import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "finance_rag")
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")


def get_vectorstore():
    embed = OllamaEmbeddings(model=EMBED_MODEL)
    chroma = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embed,
        collection_name=COLLECTION_NAME,
    )
    return chroma


def get_chroma_stats():
    chroma = get_vectorstore()
    try:
        collection = chroma._collection
        return {
            "collection_name": collection.name,
            "total_documents": collection.count(),
            "embedding_model": EMBED_MODEL,
            "llm_model": LLM_MODEL,
        }
    except Exception:
        return None


def answer_query(question: str, top_k: int = 4, temperature: float = 0.0):
    chroma = get_vectorstore()
    docs_and_scores = chroma.similarity_search_with_score(question, k=top_k)
    # Build context and sources
    context_texts = []
    sources = []
    for doc, score in docs_and_scores:
        context_texts.append(doc.page_content)
        sources.append({
            "file": doc.metadata.get("file"),
            "page": doc.metadata.get("page"),
            "score": score,
        })

    system_prompt = (
        "Answer only from the context provided below. "
        "If the context does not contain the answer, reply that the information is not available in the uploaded documents."
    )

    chat = OllamaLLM(model=LLM_MODEL, temperature=temperature)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question + "\n\nCONTEXT:\n" + "\n---\n".join(context_texts)),
    ]
    resp = chat.invoke(messages)
    # normalise response extraction across langchain versions
    if hasattr(resp, "content"):
        text = resp.content
    elif isinstance(resp, (list, tuple)) and len(resp) and hasattr(resp[0], "content"):
        text = resp[0].content
    else:
        text = str(resp)
    return text, sources
