# scripts/db_utils.py
import logging
from pymongo import MongoClient
from scripts.config import MONGO_DB_URI

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_DB_URI)
db = client["knowledge_base"]
collection = db["articles"]

def purge_database():
    result = collection.delete_many({})
    logger.info(f"Purged {result.deleted_count} documents from the database.")


def store_data(data: dict) -> None:
    if isinstance(data, dict):
        try:
            collection.insert_one(data)
            logger.info(f"Data stored for URL: {data.get('url')}")
        except Exception as e:
            logger.error(f"Failed to store data in MongoDB: {e}")
    else:
        logger.error("Data format must be a dictionary.")
