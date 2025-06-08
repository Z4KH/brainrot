from abc import ABC, abstractmethod
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiohttp
from aiohttp import ClientSession

class BaseScraper(ABC):
    def __init__(self, name: str, rate_limit: int = 1):
        """
        Initialize the base scraper.
        
        Args:
            name: Name of the scraper
            rate_limit: Number of requests per second
        """
        self.name = name
        self.rate_limit = rate_limit
        self.logger = logging.getLogger(f"scraper.{name}")
        self.session: Optional[ClientSession] = None
        self._last_request_time = 0
        
    async def __aenter__(self):
        """Setup async context."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async context."""
        if self.session:
            await self.session.close()
            
    async def _rate_limit(self):
        """Implement basic rate limiting."""
        now = datetime.now().timestamp()
        time_since_last = now - self._last_request_time
        if time_since_last < (1.0 / self.rate_limit):
            await asyncio.sleep((1.0 / self.rate_limit) - time_since_last)
        self._last_request_time = datetime.now().timestamp()
        
    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method to be implemented by child classes.
        
        Returns:
            List of scraped items as dictionaries
        """
        pass
        
    def _save_to_file(self, data: List[Dict[str, Any]], filename: str):
        """
        Save scraped data to a JSON file.
        
        Args:
            data: List of scraped items
            filename: Output filename
        """
        try:
            with open(filename, 'a', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item) + '\n')
            self.logger.info(f"Saved {len(data)} items to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving data to {filename}: {str(e)}")
            
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with rate limiting.
        
        Args:
            url: Target URL
            method: HTTP method
            **kwargs: Additional arguments for aiohttp.ClientSession.request
            
        Returns:
            Response data as dictionary
        """
        await self._rate_limit()
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            self.logger.error(f"Error making request to {url}: {str(e)}")
            return {} 