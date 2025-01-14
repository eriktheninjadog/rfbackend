import yt_dlp
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class YouTubeSearcher:
    def __init__(self):
        # Initialize yt_dlp options
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch',
        }

    def search(self, 
               query: str, 
               max_results: int = 5,
               min_duration: Optional[int] = None,
               max_duration: Optional[int] = None,
               sort_by: str = 'relevance') -> List[Dict]:
        """
        Search YouTube videos with additional filtering options.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            min_duration (int, optional): Minimum duration in seconds
            max_duration (int, optional): Maximum duration in seconds
            sort_by (str): Sort results by 'relevance', 'date', 'views', or 'duration'
            
        Returns:
            List of dictionaries containing video information
        """
        search_query = f"ytsearchdate{max_results}:{query}"
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                result = ydl.extract_info(search_query, download=False)
                
                if 'entries' not in result:
                    return []

                videos = []
                for entry in result['entries']:
                    if entry:
                        # Extract video information
                        video_info = {
                            'title': entry.get('title'),
                            'url': entry.get('webpage_url'),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'uploader': entry.get('uploader'),
                            'id': entry.get('id'),
                            'upload_date': entry.get('upload_date'),
                            'description': entry.get('description'),
                            'thumbnail': entry.get('thumbnail'),
                        }
                        
                        # Apply duration filters if specified
                        if min_duration and video_info['duration'] < min_duration:
                            continue
                        if max_duration and video_info['duration'] > max_duration:
                            continue
                            
                        videos.append(video_info)

                # Sort results based on specified criteria
                if sort_by == 'date':
                    videos.sort(key=lambda x: x['upload_date'], reverse=True)
                elif sort_by == 'views':
                    videos.sort(key=lambda x: x['view_count'], reverse=True)
                elif sort_by == 'duration':
                    videos.sort(key=lambda x: x['duration'])

                return videos[:max_results]

        except Exception as e:
            print(f"An error occurred during search: {e}")
            return []

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Convert seconds to human-readable duration."""
        return str(timedelta(seconds=seconds))

    @staticmethod
    def format_view_count(views: int) -> str:
        """Format view count with appropriate suffix."""
        if views >= 1_000_000:
            return f"{views/1_000_000:.1f}M views"
        elif views >= 1_000:
            return f"{views/1_000:.1f}K views"
        return f"{views} views"



import random

def get_sloppy_match_list():
    words = ["國經",
    "習近平",
    "面對",
    "佢地",
    "經濟",
    "真係","係"]
    searcher = YouTubeSearcher()
    ids = []
    # Search parameters
    search_query = random.choice(words) 
    search_results = searcher.search(
        query=search_query,
        max_results=100,
        min_duration=60,  # 5 minutes minimum
        max_duration=12000,  # 20 minutes maximum
        sort_by='views'    # Sort by view count
    )
    
    # Print results
    print(f"\nSearch results for: '{search_query}'\n")
    
    for i, video in enumerate(search_results, 1):
        print(f"Video {i}:")
        print(f"Title: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Duration: {YouTubeSearcher.format_duration(video['duration'])}")
        print(f"Views: {YouTubeSearcher.format_view_count(video['view_count'])}")
        print(f"Uploader: {video['uploader']}")
        print("=" * 50)
        ids.append(video['id'])
    return ids

# Example usage
def main():
    searcher = YouTubeSearcher()
    
    # Search parameters
    search_query = "冇"
    search_results = searcher.search(
        query=search_query,
        max_results=50,
        min_duration=60,  # 5 minutes minimum
        max_duration=12000,  # 20 minutes maximum
        sort_by='views'    # Sort by view count
    )
    
    # Print results
    print(f"\nSearch results for: '{search_query}'\n")
    
    for i, video in enumerate(search_results, 1):
        print(f"Video {i}:")
        print(f"Title: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Duration: {YouTubeSearcher.format_duration(video['duration'])}")
        print(f"Views: {YouTubeSearcher.format_view_count(video['view_count'])}")
        print(f"Uploader: {video['uploader']}")
        print("=" * 50)

if __name__ == "__main__":
    main()
