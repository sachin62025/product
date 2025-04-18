"""
Stack Overflow API client for fetching questions and tag data.
"""
import os
import logging
import requests
from utils.cache import cache_response

logger = logging.getLogger(__name__)

class StackOverflowClient:
    """Client for Stack Overflow API to fetch questions and tag information."""
    
    BASE_URL = "https://api.stackexchange.com/2.3"
    
    def __init__(self):
        self.api_key = os.getenv("STACKOVERFLOW_API_KEY", "")
        
    @cache_response(expires=3600)  # Cache for 1 hour
    def get_popular_questions(self, tags=None, period="week", limit=10):
        """
        Fetch popular questions from Stack Overflow.
        
        Args:
            tags (list, optional): List of tags to filter by
            period (str): Time period - 'day', 'week', or 'month'
            limit (int): Maximum number of questions to return
            
        Returns:
            list: List of popular questions with metadata
        """
        # Convert period to Stack Overflow parameter
        period_map = {
            "day": "day",
            "week": "week",
            "month": "month"
        }
        sort_period = period_map.get(period, "week")
        
        # Construct query parameters
        params = {
            "order": "desc",
            "sort": "votes",
            "site": "stackoverflow",
            "pagesize": limit,
            "filter": "!-*jbN-o8P3E5"  # Filter to include more fields
        }
        
        if self.api_key:
            params["key"] = self.api_key
            
        if tags:
            params["tagged"] = ";".join(tags)
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/questions",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            questions = []
            for question in data.get("items", []):
                questions.append({
                    "title": question["title"],
                    "link": question["link"],
                    "score": question["score"],
                    "answer_count": question["answer_count"],
                    "view_count": question["view_count"],
                    "tags": question["tags"],
                    "creation_date": question["creation_date"],
                    "is_answered": question["is_answered"]
                })
            
            return questions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching questions from Stack Overflow: {e}")
            return []
    
    @cache_response(expires=3600)
    def get_popular_tags(self, limit=20):
        """
        Get popular tags from Stack Overflow.
        
        Args:
            limit (int): Maximum number of tags to return
            
        Returns:
            list: List of popular tags with metadata
        """
        params = {
            "order": "desc",
            "sort": "popular",
            "site": "stackoverflow",
            "pagesize": limit
        }
        
        if self.api_key:
            params["key"] = self.api_key
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/tags",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant information
            tags = []
            for tag in data.get("items", []):
                tags.append({
                    "name": tag["name"],
                    "count": tag["count"],
                    "has_synonyms": tag.get("has_synonyms", False),
                    "is_moderator_only": tag.get("is_moderator_only", False),
                    "is_required": tag.get("is_required", False)
                })
            
            return tags
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching popular tags from Stack Overflow: {e}")
            return []
