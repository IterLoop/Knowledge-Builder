 
# scripts/data_pipeline.py
# Coordinates scraping, storing, and summarization steps, plus YouTube integration.

import logging
from typing import List, Optional

from scripts.scraper import scrape_webpage
from scripts.db_utils import store_data
from scripts.summarizer import summarize_text
from scripts.youtube_transcriber import youtube_search, generate_transcripts

logger = logging.getLogger(__name__)

def data_pipeline(urls: List[str]) -> Optional[str]:
    """
    Orchestrates the scraping and summarization of content from given URLs.

    :param urls: List of URLs to scrape.
    :return: Summary of all scraped text, or None if summarization fails.
    """
    collected_texts = []

    for url in urls:
        content = scrape_webpage(url)
        if content:
            data_doc = {"url": url, "content": content}
            store_data(data_doc)
            collected_texts.append(content)
        else:
            logger.error(f"No content retrieved from {url}.")

    if not collected_texts:
        logger.error("No texts collected for summarization.")
        return None

    summary = summarize_text(collected_texts)
    if summary:
        logger.info("Web pipeline completed successfully.")
        return summary
    else:
        logger.error("Web pipeline failed to produce a summary.")
        return None

def youtube_pipeline(queries: List[str], days_ago: int = 0, max_results: int = 5) -> Optional[str]:
    """
    Orchestrates searching YouTube for multiple queries, retrieving transcripts, and summarizing them.

    :param queries: List of query terms.
    :param days_ago: Relative date range in days from now.
    :param max_results: Max video results per query.
    :return: Summary of transcripts, or None if summarization fails.
    """
    video_ids = youtube_search(queries, days_ago, max_results)
    if not video_ids:
        logger.error("No videos found or invalid search query.")
        return None

    transcripts_map = generate_transcripts(video_ids)

    # Combine transcripts for summarization, skipping any that are error
    all_texts = []
    for vid, txt in transcripts_map.items():
        if not txt.startswith("Error:"):
            all_texts.append(txt)

    if not all_texts:
        logger.error("No valid transcripts found to summarize.")
        return None

    summary = summarize_text(all_texts)
    if summary:
        logger.info("YouTube pipeline completed successfully.")
        return summary
    else:
        logger.error("YouTube pipeline failed to produce a summary.")
        return None
