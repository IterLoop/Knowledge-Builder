 
import aiohttp
from bs4 import BeautifulSoup
from .base import BaseScraper

class StaticScraper(BaseScraper):
    async def scrape(self, url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                return {"content": soup.get_text()}
