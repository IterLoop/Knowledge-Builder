import logging
from scripts.data_pipeline import data_pipeline
from scripts.summarizer import summarize_and_upload
from scripts.db_utils import store_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def main():
    # Step 1: Scrape data
    test_urls = [
        "https://hbr.org/2023/11/how-global-companies-use-ai-to-prevent-supply-chain-disruptions",
        "https://www.ibm.com/think/topics/ai-supply-chain"
    ]
    logging.info("Starting data scraping...")
    scraped_texts = data_pipeline(test_urls)

    if not scraped_texts:
        logging.error("No data scraped. Exiting.")
        return

    # Step 2: Store raw content in the database
    for idx, content in enumerate(scraped_texts):
        data = {"url": test_urls[idx], "content": content, "processed": False}
        store_data(data)

    # Step 3: Summarize unprocessed content
    logging.info("Starting summarization workflow...")
    summarize_and_upload()

    logging.info("Pipeline execution completed.")

if __name__ == "__main__":
    main()
