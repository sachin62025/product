
import os
import logging
import requests
from datetime import datetime, timedelta
from utils.cache import cache_response
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()  # Load environment variables from .env file

class NewsClient:
    """Client for News API to fetch technology news articles."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            logger.warning("NEWS_API_KEY environment variable not set. Some functionality may be limited.")

    @cache_response(expires=1800)  # Cache for 30 minutes
    def get_tech_news(self, days=7, limit=10):

        if not self.api_key:
            logger.error("NEWS_API_KEY environment variable not set. Cannot fetch news.")
            return []

        # Calculate date range
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Construct query parameters
        params = {
            "apiKey": self.api_key,
            "q": "technology OR tech OR software OR programming OR AI OR 'artificial intelligence'",
            "language": "en",
            "sortBy": "popularity",
            "from": from_date,
            "to": to_date,
            "pageSize": limit
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/everything",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            # Extract relevant information
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "published_at": article.get("publishedAt", ""),
                    "content": article.get("content", "")
                })

            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching tech news: {e}")
            return []

    @cache_response(expires=3600)
    def get_technology_categories(self, limit=10):

        if not self.api_key:
            logger.error("NEWS_API_KEY environment variable not set. Cannot fetch news.")
            return {}

        categories = {
            "AI": "artificial intelligence OR AI OR machine learning OR neural network",
            "Blockchain": "blockchain OR cryptocurrency OR bitcoin OR crypto OR web3",
            "Cloud": "cloud computing OR aws OR azure OR google cloud OR saas",
            "Mobile": "mobile OR android OR ios OR app development",
            "Cybersecurity": "cybersecurity OR security OR hacking OR privacy OR data breach"
        }

        # Calculate date range
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        result = {}
        for category_name, query in categories.items():
            params = {
                "apiKey": self.api_key,
                "q": query,
                "language": "en",
                "sortBy": "popularity",
                "from": from_date,
                "to": to_date,
                "pageSize": limit
            }

            try:
                response = requests.get(
                    f"{self.BASE_URL}/everything",
                    params=params,
                    timeout=15
                )
                response.raise_for_status()
                data = response.json()

                articles = []
                for article in data.get("articles", []):
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "published_at": article.get("publishedAt", "")
                    })

                result[category_name] = articles

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching news for category {category_name}: {e}")
                result[category_name] = []

        return result