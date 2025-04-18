"""
Unit tests for API client classes.
"""
import unittest
from unittest.mock import patch, MagicMock
import os,sys
import json
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_clients.github_client import GitHubClient
from api_clients.stackoverflow_client import StackOverflowClient
from api_clients.hackernews_client import HackerNewsClient
from api_clients.news_client import NewsClient
from api_clients.reddit_client import RedditClient
from api_clients.pytrends_client import PyTrendsClient
import pandas as pd
class TestGitHubClient(unittest.TestCase):
    """Tests for GitHub API client."""
    
    @patch('requests.get')
    def test_get_trending_repositories(self, mock_get):
        """Test fetching trending repositories."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "full_name": "test/repo1",
                    "html_url": "https://github.com/test/repo1",
                    "description": "Test repository 1",
                    "language": "Python",
                    "stargazers_count": 100,
                    "forks_count": 20,
                    "created_at": "2023-01-01",
                    "topics": ["python", "testing"]
                },
                {
                    "full_name": "test/repo2",
                    "html_url": "https://github.com/test/repo2",
                    "description": "Test repository 2",
                    "language": "JavaScript",
                    "stargazers_count": 200,
                    "forks_count": 30,
                    "created_at": "2023-01-02",
                    "topics": ["javascript", "testing"]
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Create client and call method
        client = GitHubClient()
        
        # Patch the cache_response decorator to not cache in tests
        with patch('utils.cache.cache_response', lambda expires: lambda func: func):
            repos = client.get_trending_repositories(language="Python", limit=2)
        
        # Assert results
        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]['name'], "test/repo1")
        self.assertEqual(repos[0]['language'], "Python")
        self.assertEqual(repos[0]['stars'], 100)
        self.assertEqual(repos[0]['forks'], 20)
        
        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertTrue('api.github.com' in args[0])
        self.assertTrue('language:Python' in kwargs['params']['q'])
    
    @patch('requests.get')
    def test_get_language_stats(self, mock_get):
        """Test fetching language statistics."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"language": "Python"},
                {"language": "JavaScript"},
                {"language": "Python"},
                {"language": "Go"},
                {"language": "Python"},
                {"language": "JavaScript"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Create client and call method
        client = GitHubClient()
        
        # Patch the cache_response decorator to not cache in tests
        with patch('utils.cache.cache_response', lambda expires: lambda func: func):
            stats = client.get_language_stats(limit=3)
        
        # Assert results
        self.assertEqual(len(stats), 3)
        self.assertEqual(stats.get("Python"), 3)
        self.assertEqual(stats.get("JavaScript"), 2)
        self.assertEqual(stats.get("Go"), 1)


class TestStackOverflowClient(unittest.TestCase):
    """Tests for Stack Overflow API client."""
    
    @patch('requests.get')
    def test_get_popular_questions(self, mock_get):
        """Test fetching popular questions."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Test question 1",
                    "link": "https://stackoverflow.com/q/1",
                    "score": 10,
                    "answer_count": 5,
                    "view_count": 100,
                    "tags": ["python", "testing"],
                    "creation_date": 1672531200,
                    "is_answered": True
                },
                {
                    "title": "Test question 2",
                    "link": "https://stackoverflow.com/q/2",
                    "score": 20,
                    "answer_count": 8,
                    "view_count": 200,
                    "tags": ["javascript", "testing"],
                    "creation_date": 1672617600,
                    "is_answered": False
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Create client and call method
        client = StackOverflowClient()
        
        # Patch the cache_response decorator to not cache in tests
        with patch('utils.cache.cache_response', lambda expires: lambda func: func):
            questions = client.get_popular_questions(tags=["python"], limit=2)
        
        # Assert results
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]['title'], "Test question 1")
        self.assertEqual(questions[0]['score'], 10)
        self.assertEqual(questions[0]['tags'], ["python", "testing"])
        
        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertTrue('api.stackexchange.com' in args[0])
        self.assertEqual(kwargs['params']['tagged'], "python")


class TestHackerNewsClient(unittest.TestCase):
    """Tests for HackerNews API client."""
    
    @patch('requests.get')
    def test_get_top_stories(self, mock_get):
        """Test fetching top stories."""
        # Setup mock for the top stories endpoint
        top_stories_response = MagicMock()
        top_stories_response.json.return_value = [123, 456]
        top_stories_response.status_code = 200
        
        # Setup mocks for the item endpoints
        item1_response = MagicMock()
        item1_response.json.return_value = {
            "id": 123,
            "title": "Test story 1",
            "url": "https://example.com/1",
            "by": "user1",
            "score": 100,
            "time": 1672531200,
            "descendants": 10,
            "type": "story"
        }
        item1_response.status_code = 200
        
        item2_response = MagicMock()
        item2_response.json.return_value = {
            "id": 456,
            "title": "Test story 2",
            "url": "https://example.com/2",
            "by": "user2",
            "score": 200,
            "time": 1672617600,
            "descendants": 20,
            "type": "story"
        }
        item2_response.status_code = 200
        
        # Configure mock_get to return different responses for different URLs
        def mock_get_side_effect(url, **kwargs):
            if 'topstories.json' in url:
                return top_stories_response
            elif '123.json' in url:
                return item1_response
            elif '456.json' in url:
                return item2_response
            return MagicMock(status_code=404)
        
        mock_get.side_effect = mock_get_side_effect
        
        # Create client and call method
        client = HackerNewsClient()
        
        # Patch the cache_response decorator to not cache in tests
        with patch('utils.cache.cache_response', lambda expires: lambda func: func):
            stories = client.get_top_stories(limit=2)
        
        # Assert results
        self.assertEqual(len(stories), 2)
        self.assertEqual(stories[0]['id'], 123)
        self.assertEqual(stories[0]['title'], "Test story 1")
        self.assertEqual(stories[0]['score'], 100)
        self.assertEqual(stories[1]['id'], 456)
        self.assertEqual(stories[1]['title'], "Test story 2")
        self.assertEqual(stories[1]['score'], 200)


class TestNewsClient(unittest.TestCase):
    """Tests for News API client."""
    
    @patch('requests.get')
    def test_get_tech_news(self, mock_get):
        """Test fetching technology news."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test article 1",
                    "description": "Description 1",
                    "url": "https://example.com/news/1",
                    "source": {"name": "Source 1"},
                    "publishedAt": "2023-01-01T12:00:00Z",
                    "content": "Content 1"
                },
                {
                    "title": "Test article 2",
                    "description": "Description 2",
                    "url": "https://example.com/news/2",
                    "source": {"name": "Source 2"},
                    "publishedAt": "2023-01-02T12:00:00Z",
                    "content": "Content 2"
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Create client and call method
        client = NewsClient()
        
        # Set API key for testing
        client.api_key = "test_key"
        
        # Patch the cache_response decorator to not cache in tests
        with patch('utils.cache.cache_response', lambda expires: lambda func: func):
            articles = client.get_tech_news(days=7, limit=2)
        
        # Assert results
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], "Test article 1")
        self.assertEqual(articles[0]['source'], "Source 1")
        self.assertEqual(articles[1]['title'], "Test article 2")
        self.assertEqual(articles[1]['source'], "Source 2")
        
        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertTrue('newsapi.org' in args[0])
        self.assertEqual(kwargs['params']['apiKey'], "test_key")
        self.assertTrue('technology' in kwargs['params']['q'])


class TestRedditClient(unittest.TestCase):
    """Tests for Reddit API client."""
    
    @patch('requests.get')
    def test_get_top_posts(self, mock_get):
        """Test fetching top posts."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Test post 1",
                            "author": "user1",
                            "score": 100,
                            "num_comments": 10,
                            "created_utc": 1672531200,
                            "url": "https://example.com/1",
                            "permalink": "/r/technology/comments/1",
                            "selftext": "Content 1",
                            "subreddit": "technology"
                        }
                    },
                    {
                        "data": {
                            "title": "Test post 2",
                            "author": "user2",
                            "score": 200,
                            "num_comments": 20,
                            "created_utc": 1672617600,
                            "url": "https://example.com/2",
                            "permalink": "/r/technology/comments/2",
                            "selftext": "Content 2",
                            "subreddit": "technology"
                        }
                    }
                ]
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Create client and call method
        client = RedditClient()
        
        # Patch the cache_response decorator to not cache in tests
        with patch('utils.cache.cache_response', lambda expires: lambda func: func):
            posts = client.get_top_posts(subreddit="technology", limit=2)
        
        # Assert results
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]['title'], "Test post 1")
        self.assertEqual(posts[0]['score'], 100)
        self.assertEqual(posts[0]['author'], "user1")
        self.assertEqual(posts[1]['title'], "Test post 2")
        self.assertEqual(posts[1]['score'], 200)
        self.assertEqual(posts[1]['author'], "user2")
        
        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertTrue('reddit.com' in args[0])
        self.assertTrue('technology' in args[0])


class TestPyTrendsClient(unittest.TestCase):
    """Tests for PyTrends API client."""
    
    @patch('pytrends.request.TrendReq')
    def test_get_tech_trends(self, mock_trend_req):
        """Test fetching technology trends."""
        # Mock the pytrends object and its methods
        mock_pytrends = MagicMock()
        mock_trend_req.return_value = mock_pytrends
        
        # Mock the related_queries method
        mock_pytrends.related_queries.return_value = {
            'artificial intelligence': {
                'rising': pd.DataFrame({
                    'query': ['chatgpt', 'ai tools'],
                    'value': [100, 80]
                })
            },
            'machine learning': {
                'rising': pd.DataFrame({
                    'query': ['deep learning', 'neural networks'],
                    'value': [90, 70]
                })
            },
            'programming language': {'rising': pd.DataFrame({'query': [], 'value': []})},
            'blockchain': {'rising': pd.DataFrame({'query': [], 'value': []})},
            'cryptocurrency': {'rising': pd.DataFrame({'query': [], 'value': []})},
            'cloud computing': {'rising': pd.DataFrame({'query': [], 'value': []})},
            'data science': {'rising': pd.DataFrame({'query': [], 'value': []})},
            'web development': {'rising': pd.DataFrame({'query': [], 'value': []})},
            'app development': {'rising': pd.DataFrame({'query': [], 'value': []})},
            'cybersecurity': {'rising': pd.DataFrame({'query': [], 'value': []})},
        }
        
        # Create client and call method
        client = PyTrendsClient()
        client.pytrends = mock_pytrends  # Ensure the client uses the mocked pytrends object
        
        # Patch the cache_response decorator to not cache in tests
        with patch('utils.cache.cache_response', lambda expires: lambda func: func):
            trends = client.get_tech_trends(timeframe='today 3-m')
        
        # Assert results
        self.assertEqual(len(trends), 2)
        self.assertIn('artificial intelligence', trends)
        self.assertIn('machine learning', trends)
        self.assertIn('chatgpt', trends['artificial intelligence'])
        self.assertEqual(trends['artificial intelligence']['chatgpt'], 100)
        self.assertIn('ai tools', trends['artificial intelligence'])
        self.assertEqual(trends['artificial intelligence']['ai tools'], 80)
        self.assertIn('deep learning', trends['machine learning'])
        self.assertEqual(trends['machine learning']['deep learning'], 90)
        self.assertIn('neural networks', trends['machine learning'])
        self.assertEqual(trends['machine learning']['neural networks'], 70)
        
        # Verify build_payload was called correctly (for each keyword)
        self.assertEqual(mock_pytrends.build_payload.call_count, len(mock_pytrends.related_queries.return_value))

        
if __name__ == '__main__':
    unittest.main()