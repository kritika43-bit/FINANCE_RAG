import ingest
import rag


def test_shared_collection_name():
    assert hasattr(ingest, "COLLECTION_NAME")
    assert hasattr(rag, "COLLECTION_NAME")
    assert ingest.COLLECTION_NAME == rag.COLLECTION_NAME == "finance_rag"
