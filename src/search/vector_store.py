 
from langchain_community.vectorstores import Chroma
from ..core.embeddings import EmbeddingManager

class VectorStore:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.vectorstore = Chroma(
            embedding_function=self.embedding_manager.embeddings,
            persist_directory="./data/vectorstore"
        )

    async def add_texts(self, texts: list[str], metadatas: list[dict] = None):
        try:
            await self.vectorstore.aadd_texts(texts=texts, metadatas=metadatas)
        except Exception as e:
            logger.error(f"Vector store error: {e}")
            raise
