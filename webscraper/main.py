import asyncio
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from webscraper.modules.news_scraper import NewsScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)

class ScraperManager:
    def __init__(self, config_path: str = None):
        """
        Initialize the scraper manager.
        
        Args:
            config_path: Path to the configuration file
        """
        if config_path is None:
            # Get the directory where main.py is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "configs", "tickers.json")
            
        self.config_path = config_path
        self.tickers = self._load_config()
        self.scrapers = []
        
        # Ensure data directory exists
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        logger.info(f"Data directory: {self.data_dir}")
        
    def _load_config(self) -> List[str]:
        """Load ticker symbols from config file."""
        try:
            logger.info(f"Loading config from: {self.config_path}")
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                tickers = config.get("tickers", [])
                logger.info(f"Loaded {len(tickers)} tickers: {tickers}")
                return tickers
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return []
            
    async def setup_scrapers(self):
        """Initialize all scrapers."""
        logger.info("Setting up scrapers...")
        # Initialize news scraper
        news_scraper = NewsScraper(api_key=None)  # Add your API key here
        self.scrapers.append(news_scraper)
        logger.info(f"Initialized {len(self.scrapers)} scrapers")
        
    async def run_scraping_cycle(self):
        """Run one complete scraping cycle for all tickers."""
        logger.info(f"Starting scraping cycle for {len(self.tickers)} tickers")
        
        for ticker in self.tickers:
            logger.info(f"Scraping data for {ticker}")
            
            # Run all scrapers for this ticker
            for scraper in self.scrapers:
                logger.info(f"Running {scraper.name} for {ticker}")
                try:
                    async with scraper:
                        data = await scraper.scrape(query=ticker)
                        if data:
                            # Create filename with timestamp
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = os.path.join(
                                self.data_dir,
                                f"{ticker}_{scraper.name}_{timestamp}.jsonl"
                            )
                            
                            # Save data to file
                            try:
                                with open(filename, 'w', encoding='utf-8') as f:
                                    for item in data:
                                        f.write(json.dumps(item) + '\n')
                                logger.info(f"Successfully saved {len(data)} items to {filename}")
                                
                                # Verify file was created and has content
                                if os.path.exists(filename):
                                    file_size = os.path.getsize(filename)
                                    logger.info(f"File {filename} created with size {file_size} bytes")
                                else:
                                    logger.error(f"File {filename} was not created!")
                            except Exception as e:
                                logger.error(f"Error saving data to {filename}: {str(e)}")
                        else:
                            logger.warning(f"No data found for {ticker} using {scraper.name}")
                except Exception as e:
                    logger.error(f"Error running {scraper.name} for {ticker}: {str(e)}")
            
            # Add delay between tickers
            if ticker != self.tickers[-1]:  # Don't delay after the last ticker
                logger.info("Waiting 5 seconds before next ticker...")
                await asyncio.sleep(5)
                        
    async def run_continuous(self, interval_seconds: int = 300):
        """
        Run continuous scraping with specified interval.
        
        Args:
            interval_seconds: Time between scraping cycles in seconds
        """
        logger.info("Starting continuous scraping...")
        await self.setup_scrapers()
        
        while True:
            try:
                await self.run_scraping_cycle()
                logger.info(f"Completed scraping cycle. Waiting {interval_seconds} seconds...")
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in scraping cycle: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying
                
async def main():
    """Main entry point."""
    logger.info("Starting web scraper...")
    manager = ScraperManager()
    await manager.run_continuous(interval_seconds=300)  # 5 minutes between cycles
    
if __name__ == "__main__":
    asyncio.run(main()) 