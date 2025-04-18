"""
GitHub API client for fetching trending repositories and related data.
"""
import os
import logging
import requests
from datetime import datetime, timedelta
from utils.cache import cache_response

logger = logging.getLogger(__name__)

class GitHubClient:
    """Client for GitHub API to fetch trending repositories and related information."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.api_key = os.getenv("GITHUB_API_KEY", "")
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"token {self.api_key}"
        
    @cache_response(expires=3600)  # Cache for 1 hour
    def get_trending_repositories(self, language=None, since="daily", limit=10):
        """
        Fetch trending repositories from GitHub.
        
        Args:
            language (str, optional): Filter by programming language
            since (str): Time period - 'daily', 'weekly', or 'monthly'
            limit (int): Maximum number of repositories to return
            
        Returns:
            list: List of trending repositories with metadata
        """
        # Calculate date for query based on 'since' parameter
        date_ranges = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30
        }
        days = date_ranges.get(since, 1)
        date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Construct query parameters
        query_params = {
            "q": f"created:>{date}",
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }
        
        if language:
            query_params["q"] += f" language:{language}"
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/search/repositories", 
                params=query_params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            repositories = []
            for repo in data["items"][:limit]:
                repositories.append({
                    "name": repo["full_name"],
                    "url": repo["html_url"],
                    "description": repo["description"],
                    "language": repo["language"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "created_at": repo["created_at"],
                    "topics": repo.get("topics", [])
                })
            
            return repositories
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trending repositories from GitHub: {e}")
            return []
            
    @cache_response(expires=3600)
    def get_language_stats(self, limit=20):
        """
        Get statistics about programming languages from recent repositories.
        
        Args:
            limit (int): Maximum number of languages to return
            
        Returns:
            dict: Dictionary with language statistics
        """
        # Get repositories created in the last week
        date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        query_params = {
            "q": f"created:>{date}",
            "sort": "stars",
            "order": "desc",
            "per_page": 100  # Get a larger sample for better stats
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/search/repositories", 
                params=query_params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Count languages
            language_counts = {}
            for repo in data["items"]:
                language = repo["language"]
                if language:
                    language_counts[language] = language_counts.get(language, 0) + 1
            
            # Sort by count and limit
            sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            return dict(sorted_languages)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching language statistics from GitHub: {e}")
            return {}
