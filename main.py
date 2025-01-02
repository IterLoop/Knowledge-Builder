# main.py

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

def upload_to_assistant(assistant_id: str, file_path: str, purpose: str = "search"):
    """
    Upload a file to the specified assistant. The 'purpose' can be "search", "fine-tune", etc.
    """
    logging.info(f"Uploading '{file_path}' to assistant {assistant_id} with purpose={purpose}")
    with open(file_path, "rb") as f:
        response = client.beta.assistants.files.create(
            assistant_id=assistant_id,
            file=f,
            purpose=purpose
        )
    return response

def main():
    # 1) Scrape from your target URLs
    test_urls = [
        "https://hbr.org/2023/11/how-global-companies-use-ai-to-prevent-supply-chain-disruptions",
        "https://www.ibm.com/think/topics/ai-supply-chain"
    ]
    scraped_texts = data_pipeline(test_urls)

    # 2) Create local files for each piece of scraped text, then upload
    for i, content in enumerate(scraped_texts, start=1):
        if not content:
            continue
        filename = f"scraped_{i}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        # Upload to the "storage assistant"
        resp = upload_to_assistant(ASST_FOR_STORAGE, filename, purpose="search")
        logging.info(f"File {filename} -> ID: {resp.id}")
        # Optionally delete the local file
        os.remove(filename)

    # 3) YouTube pipeline
    queries = ["Supply Chain AI", "Trends in supply chain management", "Industrial AI"]
    youtube_data = youtube_pipeline(queries, days_ago=30, max_results=3, min_views=500)
    for idx, vid_meta in enumerate(youtube_data, start=1):
        # Build a .txt or .md file with metadata + transcript
        filename = f"youtube_{idx}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Title: {vid_meta['title']}\n")
            f.write(f"Channel: {vid_meta['channel']}\n")
            f.write(f"Published: {vid_meta['publish_time']}\n\n")
            f.write("Transcript:\n")
            f.write(vid_meta['transcript'])

        # Upload to "storage assistant"
        resp = upload_to_assistant(ASST_FOR_STORAGE, filename, purpose="search")
        logging.info(f"YouTube file {filename} -> ID: {resp.id}")
        os.remove(filename)

    # 4) After scraping + uploading everything, use the "writing assistant" to generate an article.
    #    We can create a "Run" or call the new Beta Assistants approach. For simplicity, let's do:
    from openai import AssistantEventHandler

    logging.info("All scraping and uploading done. Now let's have the writing assistant produce an article.")

    # Example: create a thread with a user prompt, then get a run
    # The code below depends on the new Beta Assistants approach. 
    # If you do not have these endpoints, adapt accordingly.

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Please write a single paragraph about supply chain management trends in AI in the last 30 days, referencing the knowledge in your file storage."
            }
        ]
    )
    # Now create a run with the writing assistant
    class MyEventHandler(AssistantEventHandler):
        def on_text_created(self, text) -> None:
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
