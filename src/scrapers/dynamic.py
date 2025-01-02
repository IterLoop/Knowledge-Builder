from playwright.async_api import async_playwright
from .base import BaseScraper
from loguru import logger

class DynamicScraper(BaseScraper):
    async def scrape(self, url: str) -> dict:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                content = await page.content()
                await browser.close()
                return {"content": content}
        except Exception as e:
            logger.error(f"Dynamic scraping error: {e}")
            raise
