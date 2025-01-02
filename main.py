import logging
import os
from openai import OpenAI
from scripts.config import (
    OPENAI_API_KEY,
    ASST_FOR_STORAGE,
    ASST_FOR_WRITING
)
from scripts.data_pipeline import data_pipeline, youtube_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

client = OpenAI(api_key=OPENAI_API_KEY)

TARGET_VECTOR_STORE_ID = "vs_1HzC2Y1Bd6kUKWkKbpPDCfZK"


def upload_files_to_vector_store(vector_store_id: str, file_paths: list):
    """
    Uploads multiple files to the specified existing vector store.
    Waits (polls) until the file batch is completed.
    """
    logging.info(f"Uploading {len(file_paths)} file(s) to vector store {vector_store_id}")
    
    try:
        # Prepare the file streams for upload
        with open(file_paths[0], "rb") as f:
            # Use the appropriate method for uploading files
            file_batch_response = client.beta.vector_stores.file_batches.upload(
                vector_store_id=vector_store_id,
                files=[f]
            )
        return file_batch_response
    except Exception as e:
        logging.error(f"Error uploading files: {e}")
        return None

def main():
    # 1) Scrape from your target URLs
    test_urls = [
        "https://hbr.org/2023/11/how-global-companies-use-ai-to-prevent-supply-chain-disruptions",
        "https://www.ibm.com/think/topics/ai-supply-chain"
    ]
    scraped_texts = data_pipeline(test_urls)

    # 2) Create local files for each piece of scraped text, then upload
    filenames = []
    for i, content in enumerate(scraped_texts, start=1):
        if not content:
            continue
        filename = f"scraped_{i}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        filenames.append(filename)

    if filenames:
        logging.info("Uploading scraped text files to the existing vector store...")
        upload_files_to_vector_store(TARGET_VECTOR_STORE_ID, filenames)
        # Optionally delete local files after uploading
        for filename in filenames:
            os.remove(filename)

    # 3) YouTube pipeline
    queries = ["Supply Chain AI", "Trends in supply chain management", "Industrial AI"]
    youtube_data = youtube_pipeline(queries, days_ago=30, max_results=3, min_views=500)
    
    youtube_files = []
    for idx, vid_meta in enumerate(youtube_data, start=1):
        filename = f"youtube_{idx}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Title: {vid_meta['title']}\n")
            f.write(f"Channel: {vid_meta['channel']}\n")
            f.write(f"Published: {vid_meta['publish_time']}\n\n")
            f.write("Transcript:\n")
            f.write(vid_meta['transcript'])
        youtube_files.append(filename)

    if youtube_files:
        logging.info("Uploading YouTube transcript files to the existing vector store...")
        file_batch_response = upload_files_to_vector_store(TARGET_VECTOR_STORE_ID, youtube_files)
        # For debugging, you can inspect the returned object:
        logging.info(f"File batch status: {file_batch_response.status}")
        logging.info(f"File batch counts: {file_batch_response.file_counts}")

        # Clean up local files
        for filename in youtube_files:
            os.remove(filename)

    # 4) Generate an article using the writing assistant.
    from openai import AssistantEventHandler

    logging.info("All scraping and uploading done. Now let's have the writing assistant produce an article.")

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Please write a single paragraph about supply chain management trends in AI in the last 30 days, referencing the knowledge in your file storage."
            }
        ]
    )

    class MyEventHandler(AssistantEventHandler):
        def on_text_created(self, text) -> None:
            # Streams partial text from the assistant
            print("\nassistant >", text, flush=True)

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=ASST_FOR_WRITING,
        instructions="You are an AI writing assistant. Provide a concise, single-paragraph article based on the file storage for supply chain management AI trends in the last 30 days.",
        event_handler=MyEventHandler(),
    ) as stream:
        stream.until_done()

    logging.info("Done with final article creation.")

if __name__ == "__main__":
    main()
