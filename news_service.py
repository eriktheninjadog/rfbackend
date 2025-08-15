# news_service.py

import os
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from nats_microservice import MicroserviceApp, ResultStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    description: Optional[str]
    url: str
    source: str
    author: Optional[str]
    published_at: str
    url_to_image: Optional[str]
    content: Optional[str]


@dataclass
class NewsSearchRequest:
    """Data class for news search requests"""
    keywords: List[str]
    language: str = "zh"
    sort_by: str = "relevancy"  # relevancy, popularity, publishedAt
    page_size: int = 10
    from_date: Optional[str] = None  # ISO 8601 format
    to_date: Optional[str] = None


@dataclass
class NewsSearchResponse:
    """Data class for news search responses"""
    success: bool
    total_results: int
    articles: List[NewsArticle]
    keywords_used: List[str]
    error: Optional[str] = None
    search_time: Optional[float] = None


class NewsAPIClient:
    """Client for interacting with NewsAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "X-Api-Key": api_key,
            "User-Agent": "NewsSearchMicroservice/1.0"
        })
    
    def search_articles(
        self,
        keywords: List[str],
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 10,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for news articles using NewsAPI
        
        Args:
            keywords: List of keywords to search for
            language: Language of articles
            sort_by: Sort order (relevancy, popularity, publishedAt)
            page_size: Number of articles to return
            from_date: Start date for article search
            to_date: End date for article search
            
        Returns:
            Dictionary containing search results
        """
        # Construct query string from keywords
        query = " OR ".join(f'"{keyword}"' if " " in keyword else keyword for keyword in keywords)
        
        # Build parameters
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),  # NewsAPI max is 100
        }
        
        # Add date parameters if provided
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        # Make request to NewsAPI
        try:
            response = self.session.get(
                f"{self.base_url}/everything",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request failed: {e}")
            raise
    
    def get_top_headlines(
        self,
        keywords: List[str],
        country: str = "us",
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get top headlines that match keywords
        
        Args:
            keywords: Keywords to filter headlines
            country: Country code for headlines
            category: News category
            
        Returns:
            Dictionary containing headlines
        """
        query = " ".join(keywords)
        
        params = {
            "q": query,
            "country": country,
        }
        
        if category:
            params["category"] = category
        
        try:
            response = self.session.get(
                f"{self.base_url}/top-headlines",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI headlines request failed: {e}")
            raise


class NewsSearchService:
    """News search microservice"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the news search service
        
        Args:
            api_key: NewsAPI key (can be overridden by environment variable)
        """
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("NEWS_API_KEY environment variable or api_key parameter required")
        
        self.news_client = NewsAPIClient(self.api_key)
        self.app = MicroserviceApp("news-search-service")
        
        # Register handlers
        self._register_handlers()
        
        # Statistics
        self.total_searches = 0
        self.total_articles_returned = 0
        
    def _register_handlers(self):
        """Register all service handlers"""
        
        @self.app.task("news.search", ResultStrategy.DIRECT_REPLY)
        def search_news(data: Dict[str, Any]) -> Dict[str, Any]:
            """Handle news search requests"""
            import time
            start_time = time.time()
            
            try:
                # Parse request
                keywords = data.get("keywords", [])
                if not keywords:
                    return asdict(NewsSearchResponse(
                        success=False,
                        total_results=0,
                        articles=[],
                        keywords_used=[],
                        error="No keywords provided"
                    ))
                
                # Ensure keywords is a list
                if isinstance(keywords, str):
                    keywords = [keywords]
                
                logger.info(f"Searching news for keywords: {keywords}")
                
                # Get optional parameters
                language = data.get("language", "en")
                sort_by = data.get("sort_by", "relevancy")
                page_size = data.get("page_size", 10)
                from_date = data.get("from_date")
                to_date = data.get("to_date")
                
                # If no date range specified, default to last 7 days
                if not from_date:
                    from_date = (datetime.now() - timedelta(days=7)).isoformat()
                
                # Search for articles
                result = self.news_client.search_articles(
                    keywords=keywords,
                    language=language,
                    sort_by=sort_by,
                    page_size=page_size,
                    from_date=from_date,
                    to_date=to_date
                )
                
                # Parse articles
                articles = []
                for article_data in result.get("articles", []):
                    article = NewsArticle(
                        title=article_data.get("title", ""),
                        description=article_data.get("description"),
                        url=article_data.get("url", ""),
                        source=article_data.get("source", {}).get("name", "Unknown"),
                        author=article_data.get("author"),
                        published_at=article_data.get("publishedAt", ""),
                        url_to_image=article_data.get("urlToImage"),
                        content=article_data.get("content")
                    )
                    articles.append(asdict(article))
                
                # Update statistics
                self.total_searches += 1
                self.total_articles_returned += len(articles)
                
                search_time = time.time() - start_time
                
                # Create response
                response = NewsSearchResponse(
                    success=True,
                    total_results=result.get("totalResults", len(articles)),
                    articles=articles,
                    keywords_used=keywords,
                    search_time=search_time
                )
                
                logger.info(f"Found {len(articles)} articles in {search_time:.2f}s")
                return asdict(response)
                
            except Exception as e:
                logger.error(f"Error searching news: {e}")
                return asdict(NewsSearchResponse(
                    success=False,
                    total_results=0,
                    articles=[],
                    keywords_used=keywords if 'keywords' in locals() else [],
                    error=str(e)
                ))
        
        @self.app.task("news.headlines", ResultStrategy.DIRECT_REPLY)
        def get_headlines(data: Dict[str, Any]) -> Dict[str, Any]:
            """Get top headlines matching keywords"""
            try:
                keywords = data.get("keywords", [])
                country = data.get("country", "us")
                category = data.get("category")
                
                if isinstance(keywords, str):
                    keywords = [keywords]
                
                logger.info(f"Getting headlines for keywords: {keywords}, country: {country}")
                
                result = self.news_client.get_top_headlines(
                    keywords=keywords,
                    country=country,
                    category=category
                )
                
                articles = []
                for article_data in result.get("articles", []):
                    article = NewsArticle(
                        title=article_data.get("title", ""),
                        description=article_data.get("description"),
                        url=article_data.get("url", ""),
                        source=article_data.get("source", {}).get("name", "Unknown"),
                        author=article_data.get("author"),
                        published_at=article_data.get("publishedAt", ""),
                        url_to_image=article_data.get("urlToImage"),
                        content=article_data.get("content")
                    )
                    articles.append(asdict(article))
                
                response = NewsSearchResponse(
                    success=True,
                    total_results=len(articles),
                    articles=articles,
                    keywords_used=keywords,
                )
                
                return asdict(response)
                
            except Exception as e:
                logger.error(f"Error getting headlines: {e}")
                return asdict(NewsSearchResponse(
                    success=False,
                    total_results=0,
                    articles=[],
                    keywords_used=keywords if 'keywords' in locals() else [],
                    error=str(e)
                ))
        
        @self.app.task("news.stats", ResultStrategy.DIRECT_REPLY)
        def get_statistics(data: Dict[str, Any]) -> Dict[str, Any]:
            """Get service statistics"""
            return {
                "total_searches": self.total_searches,
                "total_articles_returned": self.total_articles_returned,
                "average_articles_per_search": (
                    self.total_articles_returned / self.total_searches 
                    if self.total_searches > 0 else 0
                )
            }
        
        @self.app.startup
        def on_startup():
            logger.info("News Search Service starting up...")
            logger.info(f"Using NewsAPI with key: {self.api_key[:10]}...")
        
        @self.app.shutdown
        def on_shutdown():
            logger.info("News Search Service shutting down...")
            logger.info(f"Total searches performed: {self.total_searches}")
    
    def run(self):
        """Run the news search service"""
        self.app.run()

def main():
    """Main entry point for the news service"""
    try:
        service = NewsSearchService()
        service.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set the NEWS_API_KEY environment variable")
        logger.error("You can get a free API key at https://newsapi.org/register")
        exit(1)
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()