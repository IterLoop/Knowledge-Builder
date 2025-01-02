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
    Upload files to the vector store and poll until completion.
    """
    logging.info(f"Uploading {len(file_paths)} file(s) to vector store {vector_store_id}")
    try:
        file_streams = [open(path, "rb") for path in file_paths]
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=file_streams
        )
        logging.info(f"File batch upload complete. Status: {file_batch.status}")
        logging.info(f"File counts: {file_batch.file_counts}")
        for file_stream in file_streams:
            file_stream.close()
        return file_batch
    except Exception as e:
        logging.error(f"Error uploading files: {e}")
        return None


class MyEventHandler:
    def __init__(self):
        self.final_text = ""

    def on_text_created(self, text):
        print("\nassistant >", text, flush=True)
        self.final_text += text

    def on_done(self):
        logging.info("Final assistant output:\n" + self.final_text)


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
        logging.info("Uploading scraped text files to the vector store...")
        upload_files_to_vector_store(TARGET_VECTOR_STORE_ID, filenames)
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
        logging.info("Uploading YouTube transcript files to the vector store...")
        upload_files_to_vector_store(TARGET_VECTOR_STORE_ID, youtube_files)
        for filename in youtube_files:
            os.remove(filename)

    # 4) Generate an article using the writing assistant.
    logging.info("All scraping and uploading done. Now generating an article...")
    event_handler = MyEventHandler()
    with client.beta.threads.runs.stream(
      #  thread_id="thread_id_placeholder",  # Replace with actual thread ID
        assistant_id=ASST_FOR_WRITING,
        instructions="You are an AI writing assistant. Provide a concise, single-paragraph article based on the file storage for supply chain management AI trends in the last 30 days.",
        event_handler=event_handler,
    ) as stream:
        stream.until_done()

    logging.info("Article generation complete.")

if __name__ == "__main__":
    main()
