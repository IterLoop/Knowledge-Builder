# main.py
# Entry point demonstrating usage of the data pipeline.

import logging
from scripts.data_pipeline import data_pipeline, youtube_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

if __name__ == "__main__":
    # Example 1: Web scraping pipeline
    test_urls = [
        "https://hbr.org/2023/11/how-global-companies-use-ai-to-prevent-supply-chain-disruptions",
        "https://www.ibm.com/think/topics/ai-supply-chain"
    ]
    summary = data_pipeline(test_urls)
    if summary:
        print("Web Scraping Summary:")
        print(summary)
    else:
        print("No summary returned for web scraping pipeline.")

    # Example 2: YouTube pipeline
    queries = ["Supply Chain", "Artificial Intelligence tutorial"]
    days_ago = 30
    youtube_summary = youtube_pipeline(queries, days_ago=days_ago, max_results=3)
    if youtube_summary:
        print("\nYouTube Transcripts Summary:")
        print(youtube_summary)
    else:
        print("No summary returned for YouTube pipeline.")
