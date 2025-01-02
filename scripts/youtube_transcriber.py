 
# scripts/youtube_transcriber.py
# Searches YouTube videos by query and retrieves transcripts if available.

import logging
from typing import List, Dict, Union
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from scripts.config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)

def youtube_search(queries: List[str], days_ago: int = 0, max_results: int = 5) -> List[str]:
    """
    Search YouTube for videos matching one or multiple queries,
    uploaded within the last `days_ago` days.

    :param queries: List of search terms.
    :param days_ago: How many days ago from now to search.
    :param max_results: Maximum video results per query.
    :return: Combined list of video IDs from all queries.
    """
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "YOUR_YOUTUBE_API_KEY":
        logger.error("YouTube API key is missing or invalid.")
        return []

    today_utc = datetime.utcnow()
    published_before = today_utc.isoformat() + "Z"
    published_after = (today_utc - timedelta(days=days_ago)).isoformat() + "Z"

    logger.info(f"Searching YouTube from {published_after} to {published_before}")

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    all_video_ids = []

    for query in queries:
        logger.info(f"Searching for query: {query}")
        response = youtube.search().list(
            q=query,
            type="video",
            part="id,snippet",
            maxResults=max_results,
            publishedAfter=published_after,
            publishedBefore=published_before,
            order="date"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        all_video_ids.extend(video_ids)

    return all_video_ids

def generate_transcripts(video_ids: List[str]) -> Dict[str, Union[str, list]]:
    """
    Retrieve transcripts for a list of YouTube video IDs using youtube_transcript_api.

    :param video_ids: List of video IDs to retrieve transcripts for.
    :return: Dictionary mapping video_id -> transcript text or an error message.
    """
    transcripts = {}
    for vid in video_ids:
        try:
            data = YouTubeTranscriptApi.get_transcript(vid)
            # Combine transcript lines
            text = " ".join([item["text"] for item in data])
            transcripts[vid] = text
        except Exception as e:
            logger.error(f"Transcript unavailable for video {vid}: {e}")
            transcripts[vid] = f"Error: {str(e)}"
    return transcripts
