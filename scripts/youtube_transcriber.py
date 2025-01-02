# scripts/youtube_transcriber.py
import logging
from typing import List, Dict, Union
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from scripts.config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)

def youtube_search(
    queries: List[str],
    days_ago: int = 0,
    max_results: int = 5,
    min_views: int = 1000
) -> List[str]:
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
        # Filter by views
        if video_ids:
            stats_response = youtube.videos().list(
                part="statistics",
                id=",".join(video_ids)
            ).execute()

            filtered_video_ids = [
                item["id"]
                for item in stats_response.get("items", [])
                if int(item["statistics"].get("viewCount", 0)) >= min_views
            ]
            all_video_ids.extend(filtered_video_ids)

    return all_video_ids

def generate_transcripts(video_ids: List[str]) -> List[Dict[str, str]]:
    """
    Return a list of dictionaries like:
    [
      {
        "video_id": "...",
        "title": "...",
        "channel": "...",
        "publish_time": "...",
        "transcript": "..."
      }, ...
    ]
    """
    if not video_ids:
        return []

    # Build youtube client again to fetch snippet metadata
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    meta_response = youtube.videos().list(
        part="snippet",
        id=",".join(video_ids)
    ).execute()

    # Map video_id -> title, channel, time
    meta_map = {}
    for item in meta_response.get("items", []):
        vid = item["id"]
        snippet = item["snippet"]
        meta_map[vid] = {
            "title": snippet.get("title", "Unknown Title"),
            "channel": snippet.get("channelTitle", "Unknown Channel"),
            "publish_time": snippet.get("publishedAt", "")
        }

    results = []
    for vid in video_ids:
        video_data = {
            "video_id": vid,
            "title": meta_map.get(vid, {}).get("title", ""),
            "channel": meta_map.get(vid, {}).get("channel", ""),
            "publish_time": meta_map.get(vid, {}).get("publish_time", ""),
            "transcript": ""
        }
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(vid, languages=['en'])
            text = " ".join([item["text"] for item in transcript_data])
            video_data["transcript"] = text
        except Exception as e:
            logger.error(f"Transcript unavailable for video {vid}: {e}")
            video_data["transcript"] = f"Error: {str(e)}"
        results.append(video_data)

    return results

def main():
    """
    Example usage only. Not necessarily called from the main pipeline.
    """
    queries = ["Supply Chain", "Artificial Intelligence", "Implementation"]
    days_ago = 7
    max_results = 5
    min_views = 1000

    logger.info("Starting YouTube video search and transcript retrieval.")
    video_ids = youtube_search(queries, days_ago, max_results, min_views)
    if not video_ids:
        logger.info("No videos found for the given queries.")
        return

    transcripts = generate_transcripts(video_ids)
    for info in transcripts:
        if info["transcript"].startswith("Error:"):
            logger.info(f"Video {info['video_id']}: {info['transcript']}")
        else:
            logger.info(f"Video {info['video_id']} transcript retrieved successfully.")
            print(f"\nTitle: {info['title']}\nChannel: {info['channel']}\nTranscript:\n{info['transcript'][:300]}...\n")
