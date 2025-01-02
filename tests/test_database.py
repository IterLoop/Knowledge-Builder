# tests/test_scraping.py
import pytest
from src.scrapers.web import WebScraper
from src.scrapers.youtube import YouTubeScraper

@pytest.mark.asyncio
async def test_web_scraping():
    scraper = WebScraper()
    result = await scraper.scrape("https://example.com")
    assert "content" in result
    assert len(result["content"]) > 0

@pytest.mark.asyncio
async def test_youtube_transcript():
    scraper = YouTubeScraper("your_youtube_api_key")
    video_id = "test_video_id"
    result = await scraper.fetch_transcripts(video_id)
    assert result is not None
