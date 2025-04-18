"""
Reddit API client for fetching trending posts from technology subreddits.
"""
import os
import logging
import requests
from utils.cache import cache_response

logger = logging.getLogger(__name__)

class RedditClient:
    """Client for Reddit API to fetch trending posts from technology subreddits."""
    
    BASE_URL = "https://www.reddit.com"
    
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        self.user_agent = "python:data-alchemist:v1.0 (by /u/data_alchemist_bot)"
        self.access_token = None
        
        # If credentials are provided, authenticate
        if self.client_id and self.client_secret:
            self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate with Reddit API using client credentials flow.
        """
        try:
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            data = {
                'grant_type': 'client_credentials',
                'username': os.getenv("REDDIT_USERNAME", ""),
                'password': os.getenv("REDDIT_PASSWORD", "")
            }
            headers = {'User-Agent': self.user_agent}
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error authenticating with Reddit API: {e}")
            self.access_token = None
    
    @cache_response(expires=1800)  # Cache for 30 minutes
    def get_top_posts(self, subreddit="technology", time_filter="week", limit=10):
        """
        Fetch top posts from a subreddit.
        
        Args:
            subreddit (str): Name of the subreddit
            time_filter (str): One of "hour", "day", "week", "month", "year", "all"
            limit (int): Maximum number of posts to return
            
        Returns:
            list: List of top posts with metadata
        """
        headers = {'User-Agent': self.user_agent}
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
            base_url = "https://oauth.reddit.com"
        else:
            # If no authentication, use public API (with stricter rate limits)
            base_url = self.BASE_URL
        
        params = {
            'limit': limit,
            't': time_filter
        }
        
        try:
            response = requests.get(
                f"{base_url}/r/{subreddit}/top.json",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            posts = []
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                posts.append({
                    'title': post_data.get('title', ''),
                    'author': post_data.get('author', ''),
                    'score': post_data.get('score', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'created_utc': post_data.get('created_utc', 0),
                    'url': post_data.get('url', ''),
                    'permalink': f"{self.BASE_URL}{post_data.get('permalink', '')}",
                    'selftext': post_data.get('selftext', '')[:500],  # Truncate long text
                    'subreddit': post_data.get('subreddit', subreddit)
                })
            
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching top posts from r/{subreddit}: {e}")
            return []
    
    @cache_response(expires=3600)
    def get_tech_subreddit_posts(self, limit=5):
        """
        Fetch top posts from multiple technology-related subreddits.
        
        Args:
            limit (int): Maximum number of posts per subreddit
            
        Returns:
            dict: Dictionary of subreddits with their top posts
        """
        tech_subreddits = [
            "technology", "programming", "webdev", "artificial", 
            "MachineLearning", "datascience", "compsci", "Python",
            "javascript", "cybersecurity"
        ]
        
        result = {}
        for subreddit in tech_subreddits:
            result[subreddit] = self.get_top_posts(subreddit=subreddit, limit=limit)
        
        return result
