 
from langchain_openai import OpenAIEmbeddings
from ..config import settings

class EmbeddingManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )

    async def get_embeddings(self, text: str):
        try:
            return await self.embeddings.aembed_query(text)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise
