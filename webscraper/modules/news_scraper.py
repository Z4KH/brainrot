from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from webscraper.core.base_scraper import BaseScraper

class NewsScraper(BaseScraper):
    def __init__(self, api_key: str = None):
        """
        Initialize the news scraper.
        
        Args:
            api_key: Optional API key for news services
        """
        super().__init__(name="news_scraper", rate_limit=1)
        self.api_key = api_key
        
        # Common headers to avoid 403/429 errors
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Reliable RSS feeds
        self.sources = {
            "google_news": "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en",
            "yahoo_finance": "https://finance.yahoo.com/news/rss",
            "marketwatch": "https://www.marketwatch.com/rss/topstories",
            "investing": "https://www.investing.com/rss/news.rss",
            "seeking_alpha": "https://seekingalpha.com/feed.xml",
            "benzinga": "https://www.benzinga.com/feed"
        }
        
        self.logger.info("NewsScraper initialized")
        
    async def scrape(self, query: str = None) -> List[Dict[str, Any]]:
        """
        Scrape news from popular financial sources.
        
        Args:
            query: Search query (ticker symbol)
            
        Returns:
            List of news articles
        """
        self.logger.info(f"Starting scrape with query: {query}")
        articles = []
        
        # Scrape from each source
        for source_name, rss_url in self.sources.items():
            try:
                self.logger.info(f"Scraping {source_name}...")
                # Format URL with query if needed
                url = rss_url.format(query=query) if "{query}" in rss_url else rss_url
                
                source_articles = await self._scrape_source(source_name, url, query)
                if source_articles:
                    self.logger.info(f"Found {len(source_articles)} articles from {source_name}")
                    articles.extend(source_articles)
                await asyncio.sleep(2)  # Increased delay between sources
            except Exception as e:
                self.logger.error(f"Error scraping {source_name}: {str(e)}")
                continue
        
        # If no articles found, try Google News as fallback
        if not articles and query:
            try:
                self.logger.info("No articles found from primary sources, trying Google News fallback...")
                google_url = self.sources["google_news"].format(query=query)
                google_articles = await self._scrape_source("google_news", google_url, query)
                if google_articles:
                    self.logger.info(f"Found {len(google_articles)} articles from Google News fallback")
                    articles.extend(google_articles)
            except Exception as e:
                self.logger.error(f"Error in Google News fallback: {str(e)}")
        
        # Sort by timestamp and limit to top 10
        sorted_articles = sorted(articles, key=lambda x: x.get("timestamp", ""), reverse=True)
        return sorted_articles[:10]
        
    async def _scrape_source(self, source_name: str, rss_url: str, query: str) -> List[Dict[str, Any]]:
        """Scrape articles from a specific source."""
        try:
            async with self.session.get(rss_url, headers=self.headers, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'xml')
                    articles = []
                    
                    for item in soup.find_all('item'):
                        # Skip if article doesn't mention the query
                        if query and query.lower() not in item.title.text.lower():
                            continue
                            
                        # Get article URL
                        url = item.link.text
                        
                        # Create article object with available data
                        article = {
                            "title": item.title.text,
                            "source": source_name,
                            "timestamp": item.pubDate.text if item.pubDate else datetime.now().isoformat(),
                            "url": url,
                            "content": item.description.text if item.description else "",
                            "summary": item.description.text if item.description else ""
                        }
                        
                        # Only add if we have some content
                        if article["content"] or article["summary"]:
                            articles.append(article)
                    
                    return articles
                else:
                    self.logger.error(f"Error response from {source_name}: {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Error scraping {source_name}: {str(e)}")
            return [] 