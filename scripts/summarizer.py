# scripts/summarizer.py
import logging
from pymongo import MongoClient
from scripts.config import OPENAI_API_KEY, MONGO_DB_URI, ASST_FOR_STORAGE
from openai import OpenAI

logger = logging.getLogger(__name__)

# Database client
client_db = MongoClient(MONGO_DB_URI)
db = client_db["knowledge_base"]
collection = db["articles"]

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def purge_database():
    """
    Purge all data from the articles collection for testing purposes.
    """
    db.articles.clear()
    logger.info("Purged all documents from the database.")

def get_unprocessed_data():
    """
    Fetch fresh content from the database that hasn't been processed yet.
    """
    return collection.find({"processed": False})

def update_processed_status(document_id, summary=None):
    """
    Update a document's processed status and save summary if provided.
    """
    updates = {"processed": True}
    if summary:
        updates["summary"] = summary
    collection.update_one({"_id": document_id}, {"$set": updates})

def summarize_and_upload():
    """
    Summarize unprocessed content using the summarizer assistant.
    """
    unprocessed_data = get_unprocessed_data()
    if not unprocessed_data:
        logger.info("No unprocessed data found in the database.")
        return

    for data in unprocessed_data:
        content = data["content"]
        url = data.get("url", "Unknown URL")

        try:
            logger.info(f"Summarizing content for URL: {url}")
            # Step 1: Create a Thread
            thread = client.beta.threads.create()
            logger.info(f"Thread created with ID: {thread.id}")

            # Step 2: Add a Message to the Thread
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=content
            )

            # Step 3: Run the Assistant
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=ASST_FOR_STORAGE,
                instructions="Summarize the provided content and extract key AI trends in supply chain management.",
                event_handler=None
            ) as stream:
                stream.until_done()

            logger.info("Summarization run completed.")
            summary = "Generated summary from the assistant."  # Placeholder for actual response processing

            # Update database with the summary and mark as processed
            update_processed_status(data["_id"], summary)
        except Exception as e:
            logger.error(f"Failed to summarize content for {url}: {e}")
            update_processed_status(data["_id"])  # Mark as processed to avoid retries