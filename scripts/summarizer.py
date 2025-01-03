# scripts/summarizer.py
import logging
from pymongo import MongoClient
from scripts.config import OPENAI_API_KEY, MONGO_DB_URI, ASST_FOR_STORAGE, VECTOR_STORE_ID
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

def upload_to_vector_store(file_path):
    """
    Upload a file to the vector store and poll until completed.
    """
    with open(file_path, "rb") as file_stream:
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=VECTOR_STORE_ID,
            files=[file_stream]
        )
    logger.info(f"Uploaded file to vector store. Status: {file_batch.status}")
    print(f"File counts: {file_batch.file_counts}")

def summarize_and_upload():
    """
    Summarize unprocessed content using the summarizer assistant and upload summaries to the vector store.
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

            # Step 4: Retrieve Summary
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="assistant",
                content="Generate a summary based on the provided content."
            )
            summary = message.content
            print(f"Summary for URL {url}: {summary}")

            # Step 5: Save Summary to File
            file_name = f"summary_{url.split('/')[-1]}.txt"
            with open(file_name, "w") as f:
                f.write(summary)

            # Step 6: Upload File to Vector Store
            upload_to_vector_store(file_name)

            # Step 7: Update Database
            update_processed_status(data["_id"], summary)
        except Exception as e:
            logger.error(f"Failed to summarize content for {url}: {e}")
            update_processed_status(data["_id"])  # Mark as processed to avoid retries