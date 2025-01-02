 
from pymongo import MongoClient
from loguru import logger
from ..config import settings

class MongoDB:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client.knowledge_base
        
    async def insert_source(self, source_data):
        try:
            result = self.db.sources.insert_one(source_data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Database insertion error: {e}")
            raise
