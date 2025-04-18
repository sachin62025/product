"""
HackerNews API client for fetching top stories and related data.
"""
import logging
import requests
from utils.cache import cache_response

logger = logging.getLogger(__name__)

class HackerNewsClient:
    """Client for HackerNews API to fetch top stories and related information."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    @cache_response(expires=1800)  # Cache for 30 minutes
    def get_top_stories(self, limit=10):
        """
        Fetch top stories from HackerNews.
        
        Args:
            limit (int): Maximum number of stories to return
            
        Returns:
            list: List of top stories with metadata
        """
        try:
            # Get list of top story IDs
            response = requests.get(
                f"{self.BASE_URL}/topstories.json",
                timeout=10
            )
            response.raise_for_status()
            story_ids = response.json()[:limit]
            
            # Fetch details for each story
            stories = []
            for story_id in story_ids:
                story = self._get_item(story_id)
                if story and story.get("type") == "story":
                    stories.append({
                        "id": story["id"],
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "by": story.get("by", "anonymous"),
                        "score": story.get("score", 0),
                        "time": story.get("time", 0),
                        "descendants": story.get("descendants", 0),  # comment count
                        "type": story.get("type", "story")
                    })
            
            return stories
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching top stories from HackerNews: {e}")
            return []
    
    @cache_response(expires=3600)
    def _get_item(self, item_id):
        """
        Fetch details of a specific item (story, comment, etc.).
        
        Args:
            item_id (int): ID of the item to fetch
            
        Returns:
            dict: Item details
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/item/{item_id}.json",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching item {item_id} from HackerNews: {e}")
            return {}
    
    @cache_response(expires=3600)
    def get_tech_stories(self, limit=10):
        """
        Fetch technology-related stories by analyzing recent top stories.
        
        Args:
            limit (int): Maximum number of stories to return
            
        Returns:
            list: List of technology-related stories
        """
        # Get a larger pool of stories to filter from
        all_stories = self.get_top_stories(limit=50)
        
        # Define tech-related keywords to filter by
        tech_keywords = [
            "ai", "algorithm", "api", "app", "application", "artificial intelligence", 
            "cloud", "code", "computer", "crypto", "data", "developer", "development", 
            "digital", "framework", "github", "google", "hardware", "javascript", 
            "language", "linux", "machine learning", "microsoft", "neural", "open source", 
            "program", "programming", "python", "software", "tech", "technology", "web"
        ]
        
        # Filter stories by tech-related keywords
        tech_stories = []
        for story in all_stories:
            title_lower = story["title"].lower()
            if any(keyword in title_lower for keyword in tech_keywords):
                tech_stories.append(story)
            
            if len(tech_stories) >= limit:
                break
        
        return tech_stories
