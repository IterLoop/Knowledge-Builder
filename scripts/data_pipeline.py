# scripts/data_pipeline.py
import logging
from typing import List

from scripts.scraper import scrape_webpage
from scripts.db_utils import store_data
from scripts.youtube_transcriber import youtube_search, generate_transcripts

logger = logging.getLogger(__name__)

def data_pipeline(urls: List[str]) -> List[str]:
    """
    Scrape each URL, store in DB, return the raw texts.
    We'll handle the creation of local files + uploading outside this function.
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
    return collected_texts

def youtube_pipeline(queries: List[str], days_ago=7, max_results=5, min_views=1000):
    """
    Search YouTube, retrieve transcripts + metadata.
    Return a list of dict objects with {video_id, title, channel, publish_time, transcript}.
    """
    vids = youtube_search(queries, days_ago, max_results, min_views)
    if not vids:
        logger.error("No videos found or invalid search query.")
        return []

    data = generate_transcripts(vids)
    return data
