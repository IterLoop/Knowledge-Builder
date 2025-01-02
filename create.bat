@echo off

REM 1. Create folder structure
mkdir data
mkdir scripts
mkdir logs
mkdir secrets
mkdir notebooks

REM 2. Create files with echo or type redirection
REM    We will append content for each file.

echo. > scripts\scraper.py
echo. > scripts\db_utils.py
echo. > scripts\summarizer.py
echo. > scripts\youtube_transcriber.py
echo. > scripts\data_pipeline.py
echo. > main.py

REM 3. Populate each file with the required code

REM ========== scraper.py ==========
(
echo ^"""scraper.py
echo Handles static and JavaScript-enabled web scraping.
echo ^"""
echo import logging
echo import requests
echo from bs4 import BeautifulSoup
echo from playwright.sync_api import sync_playwright
echo from tenacity import retry, stop_after_attempt, wait_exponential
echo
echo # Configure logging for the scraper
echo logger = logging.getLogger(__name__)
echo
echo @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
echo def scrape_static_page(url: str) -> str:
echo ^    ^"""
echo ^    Scrape a static webpage using the requests library.
echo
echo ^    :param url: Target URL to scrape.
echo ^    :return: The text content of the page.
echo ^    :raises: requests.RequestException if the request fails.
echo ^    ^"""
echo ^    try:
echo ^        response = requests.get(url, timeout=10)
echo ^        response.raise_for_status()
echo ^        soup = BeautifulSoup(response.text, "html.parser")
echo ^        return soup.get_text(separator=" ", strip=True)
echo ^    except requests.RequestException as e:
echo ^        logger.error(f"Static scraper failed for {url}: {e}")
echo ^        raise
echo
echo
echo @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
echo def scrape_js_page(url: str) -> str:
echo ^    ^"""
echo ^    Scrape a JS-heavy webpage using Playwright.
echo
echo ^    :param url: Target URL to scrape.
echo ^    :return: The text content of the JS-rendered page.
echo ^    :raises: Exception if Playwright fails.
echo ^    ^"""
echo ^    try:
echo ^        with sync_playwright() as p:
echo ^            browser = p.chromium.launch(headless=True)
echo ^            page = browser.new_page()
echo ^            page.goto(url, timeout=30000)  ^REM 30s
echo ^            content = page.content()
echo ^            browser.close()
echo ^        soup = BeautifulSoup(content, "html.parser")
echo ^        return soup.get_text(separator=" ", strip=True)
echo ^    except Exception as e:
echo ^        logger.error(f"Playwright scraper failed for {url}: {e}")
echo ^        raise
echo
echo
echo def scrape_webpage(url: str) -> str:
echo ^    ^"""
echo ^    Attempt scraping statically first; if that fails, fallback to JS-based scraping.
echo
echo ^    :param url: Target URL to scrape.
echo ^    :return: Combined text from the page or None if both attempts fail.
echo ^    ^"""
echo ^    try:
echo ^        logger.info(f"Attempting static scrape for: {url}")
echo ^        return scrape_static_page(url)
echo ^    except Exception:
echo ^        logger.info(f"Static scrape failed for {url}, attempting JS scrape...")
echo ^        try:
echo ^            return scrape_js_page(url)
echo ^        except Exception as e:
echo ^            logger.error(f"All scrapers failed for {url}: {e}")
echo ^            return None
) > scripts\scraper.py

REM ========== db_utils.py ==========
(
echo ^"""db_utils.py
echo Handles MongoDB storage and retrieval operations.
echo ^"""
echo import logging
echo from pymongo import MongoClient
echo
echo # Configure logging for db operations
echo logger = logging.getLogger(__name__)
echo
echo # Establish a connection to MongoDB
echo client = MongoClient("mongodb://localhost:27017/")
echo db = client["knowledge_base"]
echo collection = db["articles"]
echo
echo def store_data(data: dict) -> None:
echo ^    ^"""
echo ^    Store a single dictionary record in MongoDB under the "articles" collection.
echo ^    :param data: A dictionary containing URL and content or other relevant fields.
echo ^    ^"""
echo ^    if isinstance(data, dict):
echo ^        try:
echo ^            collection.insert_one(data)
echo ^            logger.info(f"Data stored for URL: {data.get('url')}")
echo ^        except Exception as e:
echo ^            logger.error(f"Failed to store data in MongoDB: {e}")
echo ^    else:
echo ^        logger.error("Data format not compatible for storage (must be a dict).")
) > scripts\db_utils.py

REM ========== summarizer.py ==========
(
echo ^"""summarizer.py
echo Summarizes text using OpenAI GPT-4.
echo ^"""
echo import os
echo import logging
echo import openai
echo from typing import List, Optional
echo
echo # Configure logging
echo logger = logging.getLogger(__name__)
echo
echo # Set your OpenAI API key securely (use environment variables or a secrets manager in production).
echo openai.api_key = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
echo
echo def summarize_text(texts: List[str]) -> Optional[str]:
echo ^    ^"""
echo ^    Summarize a list of text strings using OpenAI's ChatCompletion (GPT-4).
echo
echo ^    :param texts: List of text contents to summarize.
echo ^    :return: A summary string, or None on failure.
echo ^    ^"""
echo ^    try:
echo ^        combined_text = " ".join(texts)
echo ^        logger.info("Sending text to GPT-4 for summarization...")
echo ^        response = openai.ChatCompletion.create(
echo ^            model="gpt-4",
echo ^            messages=[
echo ^                {"role": "system", "content": "You are a helpful assistant summarizing content."},
echo ^                {"role": "user", "content": combined_text}
echo ^            ]
echo ^        )
echo ^        summary = response["choices"][0]["message"]["content"]
echo ^        logger.info("Received summary from GPT-4.")
echo ^        return summary
echo ^    except Exception as e:
echo ^        logger.error(f"Failed to summarize: {e}")
echo ^        return None
) > scripts\summarizer.py

REM ========== youtube_transcriber.py ==========
(
echo ^"""youtube_transcriber.py
echo Searches YouTube videos by query and date range; retrieves transcripts if available.
echo ^"""
echo import os
echo import logging
echo from typing import List, Dict, Union
echo from datetime import datetime, timedelta
echo
echo from googleapiclient.discovery import build
echo from youtube_transcript_api import YouTubeTranscriptApi
echo
echo # Configure logging
echo logger = logging.getLogger(__name__)
echo
echo # Set your YouTube API key securely (use environment variables or a secrets manager in production).
echo YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")
echo
echo def youtube_search(queries: List[str],
echo ^                  days_ago: int = 0,
echo ^                  max_results: int = 5) -> List[str]:
echo ^    ^"""
echo ^    Searches YouTube for videos matching one or multiple queries uploaded within the last `days_ago` days.
echo
echo ^    :param queries: List of search terms.
echo ^    :param days_ago: How many days ago from today to consider.
echo ^    :param max_results: Maximum number of video results per query.
echo ^    :return: Combined list of video IDs from all queries.
echo ^    ^"""
echo ^    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY":
echo ^        logger.error("YouTube API key is missing or invalid.")
echo ^        return []
echo
echo ^    today_utc = datetime.utcnow()
echo ^    published_before = today_utc.isoformat() + "Z"
echo ^    published_after = (today_utc - timedelta(days=days_ago)).isoformat() + "Z"
echo
echo ^    logger.info(f"Searching YouTube from {published_after} to {published_before}")
echo
echo ^    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
echo ^    all_video_ids = []
echo
echo ^    for query in queries:
echo ^        logger.info(f"Searching for query: {query}")
echo ^        search_response = youtube.search().list(
echo ^            q=query,
echo ^            type="video",
echo ^            part="id,snippet",
echo ^            maxResults=max_results,
echo ^            publishedAfter=published_after,
echo ^            publishedBefore=published_before,
echo ^            order="date"  ^REM sorts by recent uploads
echo ^        ).execute()
echo
echo ^        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
echo ^        all_video_ids.extend(video_ids)
echo
echo ^    return all_video_ids
echo
echo def generate_transcripts(video_ids: List[str]) -> Dict[str, Union[str, list]]:
echo ^    ^"""
echo ^    Retrieves transcripts for a list of YouTube video IDs using the youtube_transcript_api.
echo
echo ^    :param video_ids: List of video IDs to retrieve transcripts.
echo ^    :return: Dictionary mapping video ID to transcript text or an error message.
echo ^    ^"""
echo ^    transcripts = {}
echo ^    for video_id in video_ids:
echo ^        try:
echo ^            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
echo ^            # Convert transcript_data (list of dicts) into a single text string
echo ^            # Example: "[00:00] Hello world. [00:05] This is a transcript..."
echo ^            transcript_text = " ".join([entry["text"] for entry in transcript_data])
echo ^            transcripts[video_id] = transcript_text
echo ^        except Exception as e:
echo ^            logger.error(f"Transcript unavailable for video {video_id}: {e}")
echo ^            transcripts[video_id] = f"Error: {str(e)}"
echo ^    return transcripts
) > scripts\youtube_transcriber.py

REM ========== data_pipeline.py ==========
(
echo ^"""data_pipeline.py
echo Coordinates the scraping of web pages, storage, and summarization steps.
echo Also includes optional YouTube search + transcription integration.
echo ^"""
echo import logging
echo from typing import List, Optional
echo
echo from scripts.scraper import scrape_webpage
echo from scripts.db_utils import store_data
echo from scripts.summarizer import summarize_text
echo from scripts.youtube_transcriber import youtube_search, generate_transcripts
echo
echo # Configure logging
echo logger = logging.getLogger(__name__)
echo
echo def data_pipeline(urls: List[str]) -> Optional[str]:
echo ^    ^"""
echo ^    Orchestrates the web scraping, storing, and summarizing of content from given URLs.
echo
echo ^    :param urls: List of URLs to scrape.
echo ^    :return: Summary of all scraped text, or None if summarization fails.
echo ^    ^"""
echo ^    collected_texts = []
echo ^    for url in urls:
echo ^        content = scrape_webpage(url)
echo ^        if content:
echo ^            data_doc = {"url": url, "content": content}
echo ^            store_data(data_doc)
echo ^            collected_texts.append(content)
echo ^        else:
echo ^            logger.error(f"No content retrieved from {url}.")
echo
echo ^    if not collected_texts:
echo ^        logger.error("No texts were collected for summarization.")
echo ^        return None
echo
echo ^    summary = summarize_text(collected_texts)
echo ^    if summary:
echo ^        logger.info("Data pipeline (web scraping) completed successfully.")
echo ^        return summary
echo ^    else:
echo ^        logger.error("Data pipeline failed to produce a summary.")
echo ^        return None
echo
echo def youtube_pipeline(queries: List[str], days_ago: int = 0, max_results: int = 5) -> Optional[str]:
echo ^    ^"""
echo ^    Orchestrates searching YouTube for multiple queries, retrieving transcripts, storing them,
echo ^    and summarizing the combined transcripts.
echo
echo ^    :param queries: List of query terms.
echo ^    :param days_ago: How many days ago to start the search from (relative date).
echo ^    :param max_results: Max video results per query.
echo ^    :return: Summary of all transcripts, or None if summarization fails.
echo ^    ^"""
echo ^    all_video_ids = youtube_search(queries, days_ago, max_results)
echo ^    if not all_video_ids:
echo ^        logger.error("No videos found or invalid search query.")
echo ^        return None
echo
echo ^    transcripts_map = generate_transcripts(all_video_ids)
echo ^    # Store each transcript in the DB (optional or in a separate collection).
echo ^    # For example:
echo ^    # from scripts.db_utils import db
echo ^    # video_collection = db["youtube_videos"]
echo ^    # ...
echo
echo ^    # Combine all transcripts into a list for summarization
echo ^    all_texts = []
echo ^    for vid, text in transcripts_map.items():
echo ^        # If there's an error, skip it or handle differently
echo ^        if not text.startswith("Error:"):
echo ^            all_texts.append(text)
echo
echo ^    if not all_texts:
echo ^        logger.error("No valid transcripts found to summarize.")
echo ^        return None
echo
echo ^    summary = summarize_text(all_texts)
echo ^    if summary:
echo ^        logger.info("YouTube pipeline completed successfully.")
echo ^        return summary
echo ^    else:
echo ^        logger.error("YouTube pipeline failed to produce a summary.")
echo ^        return None
) > scripts\data_pipeline.py

REM ========== main.py ==========
(
echo ^"""main.py
echo Entry point to demonstrate and test the pipelines.
echo ^"""
echo import logging
echo from scripts.data_pipeline import data_pipeline, youtube_pipeline
echo
echo # Basic logging setup for console output
echo logging.basicConfig(
echo ^    level=logging.INFO,
echo ^    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
echo ^    handlers=[
echo ^        logging.StreamHandler()
echo ^    ]
echo )
echo
echo if __name__ == "__main__":
echo ^    # Example 1: Web scraping pipeline
echo ^    test_urls = [
echo ^        "https://example.com/article1",
echo ^        "https://example.com/article2"
echo ^    ]
echo ^    summary = data_pipeline(test_urls)
echo ^    if summary:
echo ^        print("Web Scraping Summary:")
echo ^        print(summary)
echo ^    else:
echo ^        print("Data pipeline failed to produce a summary for web pages.")
echo
echo ^    # Example 2: YouTube search + transcript pipeline
echo ^    queries = ["Python programming", "ChatGPT tutorial"]
echo ^    days_ago = 30  ^REM Search videos published in the last 30 days
echo ^    youtube_summary = youtube_pipeline(queries, days_ago=days_ago, max_results=3)
echo ^    if youtube_summary:
echo ^        print("\nYouTube Transcripts Summary:")
echo ^        print(youtube_summary)
echo ^    else:
echo ^        print("YouTube pipeline failed to produce a summary.")
) > main.py

echo All project files have been created successfully!
echo.
echo To proceed, remember to install necessary packages, e.g.:
echo   pip install requests beautifulsoup4 playwright tenacity pymongo openai tiktoken google-api-python-client youtube_transcript_api
echo   playwright install
echo.
echo Done!
