# news_client.py

import os
import sys
import json
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from nats_microservice import create_publisher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsClient:
    """Client for interacting with the news search service"""
    
    def __init__(self):
        """Initialize the news client"""
        self.client = create_publisher("news-client")
        logger.info("News client initialized")
    
    def search_news(
        self,
        keywords: List[str],
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 10,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ):
        """
        Search for news articles
        
        Args:
            keywords: List of keywords to search for
            language: Language of articles
            sort_by: Sort order
            page_size: Number of articles to return
            from_date: Start date for search
            to_date: End date for search
            
        Returns:
            Search results
        """
        request_data = {
            "keywords": keywords,
            "language": language,
            "sort_by": sort_by,
            "page_size": page_size
        }
        
        if from_date:
            request_data["from_date"] = from_date
        if to_date:
            request_data["to_date"] = to_date
        
        logger.info(f"Searching for news with keywords: {keywords}")
        
        result = self.client.request_reply("news.search", request_data, timeout=15.0)
        
        if result and result.get("success"):
            return result
        else:
            logger.error(f"Search failed: {result.get('error') if result else 'No response'}")
            return None
    
    def get_headlines(
        self,
        keywords: List[str],
        country: str = "us",
        category: Optional[str] = None
    ):
        """
        Get top headlines
        
        Args:
            keywords: Keywords to filter headlines
            country: Country code
            category: News category
            
        Returns:
            Headlines results
        """
        request_data = {
            "keywords": keywords,
            "country": country
        }
        
        if category:
            request_data["category"] = category
        
        logger.info(f"Getting headlines for keywords: {keywords}")
        
        result = self.client.request_reply("news.headlines", request_data, timeout=10.0)
        
        if result and result.get("success"):
            return result
        else:
            logger.error(f"Headlines request failed: {result.get('error') if result else 'No response'}")
            return None
    
    def get_stats(self):
        """Get service statistics"""
        result = self.client.request_reply("news.stats", {}, timeout=5.0)
        return result
    
    def close(self):
        """Close the client connection"""
        self.client.stop()
        logger.info("News client closed")


def print_article(article: dict, index: int):
    """Pretty print an article"""
    print(f"\n--- Article {index + 1} ---")
    print(f"Title: {article['title']}")
    print(f"Source: {article['source']}")
    print(f"Published: {article['published_at']}")
    if article.get('author'):
        print(f"Author: {article['author']}")
    if article.get('description'):
        print(f"Description: {article['description'][:200]}...")
    print(f"URL: {article['url']}")


def interactive_mode():
    """Run the client in interactive mode"""
    client = NewsClient()
    
    print("\n=== News Search Client ===")
    print("Commands:")
    print("  search <keyword1> <keyword2> ... - Search for news articles")
    print("  headlines <keyword1> <keyword2> ... - Get top headlines")
    print("  stats - Get service statistics")
    print("  quit - Exit the client")
    print()
    
    try:
        while True:
            try:
                command = input("Enter command: ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    break
                
                elif cmd == "search":
                    if len(parts) < 2:
                        print("Usage: search <keyword1> <keyword2> ...")
                        continue
                    
                    keywords = parts[1:]
                    result = client.search_news(keywords, page_size=5)
                    
                    if result:
                        print(f"\nFound {result['total_results']} total results")
                        print(f"Showing {len(result['articles'])} articles:")
                        
                        for i, article in enumerate(result['articles']):
                            print_article(article, i)
                        
                        if result.get('search_time'):
                            print(f"\nSearch completed in {result['search_time']:.2f} seconds")
                    else:
                        print("Search failed")
                
                elif cmd == "headlines":
                    if len(parts) < 2:
                        print("Usage: headlines <keyword1> <keyword2> ...")
                        continue
                    
                    keywords = parts[1:]
                    result = client.get_headlines(keywords)
                    
                    if result:
                        print(f"\nFound {len(result['articles'])} headlines:")
                        
                        for i, article in enumerate(result['articles']):
                            print_article(article, i)
                    else:
                        print("Failed to get headlines")
                
                elif cmd == "stats":
                    stats = client.get_stats()
                    if stats:
                        print("\n=== Service Statistics ===")
                        print(f"Total searches: {stats['total_searches']}")
                        print(f"Total articles returned: {stats['total_articles_returned']}")
                        print(f"Average articles per search: {stats['average_articles_per_search']:.2f}")
                    else:
                        print("Failed to get statistics")
                
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    finally:
        client.close()


def demo_mode():
    """Run a demonstration of the news client"""
    client = NewsClient()
    
    try:
        print("\n=== News Search Service Demo ===\n")
        
        # Example 1: Search for technology news
        print("1. Searching for technology news...")
        result = client.search_news(
            keywords=["artificial intelligence", "machine learning"],
            page_size=3,
            sort_by="popularity"
        )
        
        if result and result['success']:
            print(f"   Found {result['result']['total_results']} articles about AI/ML")
            for i, article in enumerate(result['result']['articles'][:3]):
                print(f"   - {article['title'][:80]}...")
        
        print()
        
        # Example 2: Search for recent news
        print("2. Searching for recent climate news...")
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        result = client.search_news(
            keywords=["climate change", "global warming"],
            page_size=3,
            from_date=yesterday
        )
        
        if result and result['success']:
            print(f"   Found {len(result['result']['articles'])} recent articles about climate")
            for article in result['result']['articles'][:3]:
                print(f"   - {article['title'][:80]}...")
        
        print()
        
        # Example 3: Get headlines
        print("3. Getting top US headlines about economy...")
        result = client.get_headlines(
            keywords=["economy"],
            country="us"
        )
        
        if result and result['success']:
            print(f"   Found {len(result['result']['articles'])} headlines")
            for article in result['result']['articles'][:3]:
                print(f"   - {article['title'][:80]}...")
        
        print()
        
        # Example 4: Get service statistics
        print("4. Getting service statistics...")
        stats = client.get_stats()
        if stats:
            print(f"   Total searches performed: {stats['result']['total_searches']}")
            print(f"   Total articles returned: {stats['result']['total_articles_returned']}")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        client.close()


def main():
    """Main entry point for the news client"""
    import argparse
    
    parser = argparse.ArgumentParser(description="News Search Client")
    parser.add_argument(
        "mode",
        choices=["interactive", "demo", "search"],
        help="Mode to run the client in"
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Keywords for search mode"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language for articles"
    )
    parser.add_argument(
        "--sort-by",
        choices=["relevancy", "popularity", "publishedAt"],
        default="relevancy",
        help="Sort order for results"
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=10,
        help="Number of articles to return"
    )
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_mode()
    elif args.mode == "demo":
        demo_mode()
    elif args.mode == "search":
        if not args.keywords:
            print("Error: --keywords required for search mode")
            sys.exit(1)
        
        client = NewsClient()
        try:
            result = client.search_news(
                keywords=args.keywords,
                language=args.language,
                sort_by=args.sort_by,
                page_size=args.page_size
            )
            
            if result and result['success']:
                print(f"\nFound {result['total_results']} articles")
                for i, article in enumerate(result['articles']):
                    print_article(article, i)
            else:
                print("Search failed")
        finally:
            client.close()


if __name__ == "__main__":
    main()