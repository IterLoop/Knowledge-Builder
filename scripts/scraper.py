# scripts/scraper.py
import logging
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def scrape_static_page(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except requests.RequestException as e:
        logger.error(f"Static scraper failed for {url}: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def scrape_js_page(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            content = page.content()
            browser.close()
        soup = BeautifulSoup(content, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        logger.error(f"Playwright scraper failed for {url}: {e}")
        raise

def scrape_webpage(url: str) -> str:
    try:
        logger.info(f"Attempting static scrape for: {url}")
        data = scrape_static_page(url)
        logger.info(f"[SCRAPER] Static content (first 200 chars): {data[:200]!r}")
        return data
    except Exception:
        logger.info(f"Static scrape failed for {url}, attempting JS scrape...")
        try:
            data = scrape_js_page(url)
            logger.info(f"[SCRAPER] JS-based content (first 200 chars): {data[:200]!r}")
            return data
        except Exception as e:
            logger.error(f"All scrapers failed for {url}: {e}")
            return ""
