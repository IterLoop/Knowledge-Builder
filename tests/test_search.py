 
# tests/test_search.py
import pytest
from src.search.vector_store import VectorStore

def test_vector_store_connection():
    store = VectorStore("your_vector_db_config")
    assert store.client is not None

@pytest.mark.asyncio
async def test_embedding_storage():
    store = VectorStore("your_vector_db_config")
    test_data = {"text": "test content"}
    test_vector = [0.1] * 1536  # OpenAI embedding dimension
    await store.store_embeddings(test_data, test_vector)
