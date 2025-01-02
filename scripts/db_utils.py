 
# scripts/db_utils.py
# Handles MongoDB storage operations.

import logging
from pymongo import MongoClient
from scripts.config import MONGO_DB_URI

logger = logging.getLogger(__name__)

# Establish a connection to MongoDB using MONGO_DB_URI from config.py
client = MongoClient(MONGO_DB_URI)
db = client["knowledge_base"]
collection = db["articles"]

def store_data(data: dict) -> None:
    """
    Stores a single dictionary in the 'articles' collection.

    :param data: Dictionary containing, for example, 'url' and 'content'.
    """
    if isinstance(data, dict):
        try:
            collection.insert_one(data)
            logger.info(f"Data stored for URL: {data.get('url')}")
        except Exception as e:
            logger.error(f"Failed to store data in MongoDB: {e}")
    else:
        logger.error("Data format must be a dictionary.")
