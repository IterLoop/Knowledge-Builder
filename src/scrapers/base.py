from abc import ABC, abstractmethod
import pybreaker
from loguru import logger

class BaseScraper(ABC):
    def __init__(self):
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=5,
            reset_timeout=60
        )

    @abstractmethod
    async def scrape(self, url: str) -> dict:
        pass
