"""
Unit tests for the data processor module.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os , sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing.processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """Tests for the DataProcessor class."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a processor with mocked API clients
        self.processor = DataProcessor()
        
        # Create mocks for each API client
        self.processor.github_client = MagicMock()
        self.processor.stackoverflow_client = MagicMock()
        self.processor.hackernews_client = MagicMock()
        self.processor.news_client = MagicMock()
        self.processor.reddit_client = MagicMock()
        self.processor.pytrends_client = MagicMock()
    
    def test_get_technology_popularity(self):
        """Test getting technology popularity data."""
        # Setup mock data
        self.processor.github_client.get_language_stats.return_value = {
            "python": 100,
            "javascript": 80,
            "rust": 40
        }
        
        self.processor.stackoverflow_client.get_popular_tags.return_value = [
            {"name": "python", "count": 50000},
            {"name": "javascript", "count": 40000},
            {"name": "java", "count": 30000}
        ]
        
        self.processor.pytrends_client.get_trending_technologies.return_value = [
            {"name": "Python", "category": "programming languages", "popularity": 80},
            {"name": "JavaScript", "category": "programming languages", "popularity": 70},
            {"name": "React", "category": "web frameworks", "popularity": 60}
        ]
        
        # Call the method
        result = self.processor.get_technology_popularity()
        
        # Assert results
        self.assertIsInstance(result, dict)
        self.assertTrue("python" in result)
        self.assertTrue("javascript" in result)
        self.assertTrue("rust" in result)
        self.assertTrue("java" in result)
        self.assertTrue("react" in result)
        
        # Check structure of result
        for tech, data in result.items():
            self.assertIn("overall_score", data)
            self.assertIn("platform_scores", data)
            self.assertIn("github", data["platform_scores"])
            self.assertIn("stackoverflow", data["platform_scores"])
            self.assertIn("pytrends", data["platform_scores"])
    
    def test_get_trending_topics(self):
        """Test getting trending topics data."""
        # Setup mock data
        self.processor.news_client.get_tech_news.return_value = [
            {
                "title": "New AI breakthrough by OpenAI",
                "description": "OpenAI released a new model called GPT-4.",
                "url": "https://example.com/news/1",
                "source": "Tech News",
                "published_at": "2023-01-01T12:00:00Z"
            },
            {
                "title": "Google announces new cloud services",
                "description": "Google Cloud expands its offerings with new ML tools.",
                "url": "https://example.com/news/2",
                "source": "Cloud News",
                "published_at": "2023-01-02T12:00:00Z"
            }
        ]
        
        self.processor.reddit_client.get_tech_subreddit_posts.return_value = {
            "technology": [
                {
                    "title": "OpenAI's GPT-4 is amazing for coding",
                    "permalink": "/r/technology/comments/1",
                    "score": 1000,
                    "num_comments": 200,
                    "subreddit": "technology"
                }
            ],
            "programming": [
                {
                    "title": "Rust vs Go: A performance comparison",
                    "permalink": "/r/programming/comments/2",
                    "score": 500,
                    "num_comments": 150,
                    "subreddit": "programming"
                }
            ]
        }
        
        self.processor.hackernews_client.get_tech_stories.return_value = [
            {
                "title": "GPT-4 Technical Report",
                "url": "https://example.com/hn/1",
                "score": 500
            },
            {
                "title": "The future of cloud computing",
                "url": "https://example.com/hn/2",
                "score": 300
            }
        ]
        
        # Call the method
        result = self.processor.get_trending_topics()
        
        # Assert results
        self.assertIsInstance(result, dict)
        
        # Given the mock data, we should have topics related to GPT-4, AI, and cloud
        topic_names = list(result.keys())
        
        # At least some of these should be in the results (exact topic extraction may vary)
        potential_topics = ["gpt-4", "openai", "ai", "cloud", "google", "rust", "go"]
        found_topics = [topic for topic in potential_topics if any(topic in t.lower() for t in topic_names)]
        
        self.assertTrue(len(found_topics) > 0, "No expected topics found in the results")
        
        # Check structure of result
        for topic, data in result.items():
            self.assertIn("sources", data)
            self.assertIn("source_count", data)
            self.assertGreaterEqual(data["source_count"], 1)
            
            for source in data["sources"]:
                self.assertIn("source_type", source)
                self.assertIn("title", source)
                self.assertIn("url", source)
    
    def test_get_emerging_repositories(self):
        """Test getting emerging repositories data."""
        # Setup mock data
        self.processor.get_technology_popularity = MagicMock(return_value={
            "python": {"overall_score": 90, "platform_scores": {}},
            "javascript": {"overall_score": 85, "platform_scores": {}},
            "rust": {"overall_score": 70, "platform_scores": {}}
        })
        
        self.processor.github_client.get_trending_repositories.side_effect = lambda language, **kwargs: [
            {
                "name": f"user/{language.lower()}-project",
                "description": f"A cool {language} project",
                "language": language,
                "stars": 1000,
                "forks": 100,
                "url": f"https://github.com/user/{language.lower()}-project",
                "created_at": "2023-01-01",
                "topics": [language.lower(), "cool-project"]
            },
            {
                "name": f"org/{language.lower()}-lib",
                "description": f"A useful {language} library",
                "language": language,
                "stars": 500,
                "forks": 50,
                "url": f"https://github.com/org/{language.lower()}-lib",
                "created_at": "2023-01-02",
                "topics": [language.lower(), "library"]
            }
        ] if language else []
        
        # Call the method
        result = self.processor.get_emerging_repositories()
        
        # Assert results
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Check that repositories are related to trending technologies
        for repo in result:
            self.assertIn("name", repo)
            self.assertIn("description", repo)
            self.assertIn("language", repo)
            self.assertIn("stars", repo)
            self.assertIn("forks", repo)
            self.assertIn("url", repo)
            self.assertIn("created_at", repo)
            self.assertIn("topics", repo)
            self.assertIn("related_technology", repo)
    
    def test_get_hot_discussions(self):
        """Test getting hot discussions data."""
        # Setup mock data
        self.processor.get_technology_popularity = MagicMock(return_value={
            "python": {"overall_score": 90, "platform_scores": {}},
            "javascript": {"overall_score": 85, "platform_scores": {}},
            "rust": {"overall_score": 70, "platform_scores": {}}
        })
        
        self.processor.stackoverflow_client.get_popular_questions.side_effect = lambda tags, **kwargs: [
            {
                "title": f"How to do X in {tags[0]}?",
                "link": f"https://stackoverflow.com/q/{tags[0]}/1",
                "score": 50,
                "answer_count": 5,
                "view_count": 1000,
                "tags": [tags[0], "programming"]
            },
            {
                "title": f"Best practices for {tags[0]} development",
                "link": f"https://stackoverflow.com/q/{tags[0]}/2",
                "score": 30,
                "answer_count": 3,
                "view_count": 800,
                "tags": [tags[0], "best-practices"]
            }
        ] if tags else []
        
        self.processor.reddit_client.get_top_posts.side_effect = lambda subreddit, **kwargs: [
            {
                "title": f"Python is amazing for data science",
                "permalink": f"/r/{subreddit}/comments/1",
                "score": 500,
                "num_comments": 100,
                "subreddit": subreddit
            },
            {
                "title": f"JavaScript frameworks comparison",
                "permalink": f"/r/{subreddit}/comments/2",
                "score": 300,
                "num_comments": 80,
                "subreddit": subreddit
            }
        ]
        
        # Call the method
        result = self.processor.get_hot_discussions()
        
        # Assert results
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Check structure of result
        for discussion in result:
            self.assertIn("title", discussion)
            self.assertIn("url", discussion)
            self.assertIn("source", discussion)
            self.assertIn("engagement_score", discussion)
            
            if "stackoverflow" in discussion["source"]:
                self.assertIn("score", discussion)
                self.assertIn("answer_count", discussion)
                self.assertIn("view_count", discussion)
            else:  # Reddit
                self.assertIn("score", discussion)
                self.assertIn("comment_count", discussion)
    
    def test_get_technology_correlations(self):
        """Test getting technology correlations data."""
        # Setup mock data for trending technologies
        self.processor.get_technology_popularity = MagicMock(return_value={
            "python": {"overall_score": 90, "platform_scores": {}},
            "javascript": {"overall_score": 85, "platform_scores": {}},
            "react": {"overall_score": 75, "platform_scores": {}},
            "aws": {"overall_score": 80, "platform_scores": {}}
        })
        
        # Mock GitHub repositories with technologies mentioned in descriptions and topics
        self.processor.github_client.get_trending_repositories.return_value = [
            {
                "name": "user/project1",
                "description": "A Python and JavaScript project",
                "language": "Python",
                "topics": ["python", "javascript", "web"]
            },
            {
                "name": "user/project2",
                "description": "React with AWS integration",
                "language": "JavaScript",
                "topics": ["react", "aws", "frontend"]
            },
            {
                "name": "user/project3",
                "description": "Python for AWS",
                "language": "Python",
                "topics": ["python", "aws", "cloud"]
            }
        ]
        
        # Mock Stack Overflow questions with technology tags
        self.processor.stackoverflow_client.get_popular_questions.side_effect = lambda tags, **kwargs: [
            {
                "title": f"Question about {tags[0]}",
                "link": f"https://stackoverflow.com/q/{tags[0]}/1",
                "tags": [tags[0], "javascript"] if tags[0] != "javascript" else [tags[0], "react"]
            },
            {
                "title": f"How to use {tags[0]}",
                "link": f"https://stackoverflow.com/q/{tags[0]}/2",
                "tags": [tags[0], "aws"] if tags[0] != "aws" else [tags[0], "python"]
            }
        ] if tags else []
        
        # Call the method
        result = self.processor.get_technology_correlations()
        
        # Assert results
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)
        
        # Check for expected correlations based on mock data
        expected_correlations = [
            ("python", "javascript"),
            ("python", "aws"),
            ("javascript", "react"),
            ("react", "aws")
        ]
        
        for tech1, tech2 in expected_correlations:
            # Check correlation exists in both directions
            self.assertIn(tech1, result)
            self.assertIn(tech2, result[tech1])
            self.assertIn(tech2, result)
            self.assertIn(tech1, result[tech2])
            
            # Correlation should be positive
            self.assertGreater(result[tech1][tech2], 0)
            self.assertEqual(result[tech1][tech2], result[tech2][tech1])  # Symmetric
    
    def test_get_technology_insights_report(self):
        """Test getting a comprehensive technology insights report."""
        # Mock all the component methods
        self.processor.get_technology_popularity = MagicMock(return_value={
            "python": {"overall_score": 90, "platform_scores": {"github": 80, "stackoverflow": 90, "pytrends": 100}},
            "javascript": {"overall_score": 85, "platform_scores": {"github": 85, "stackoverflow": 85, "pytrends": 85}},
            "rust": {"overall_score": 70, "platform_scores": {"github": 60, "stackoverflow": 70, "pytrends": 80}}
        })
        
        self.processor.get_trending_topics = MagicMock(return_value={
            "ai": {"source_count": 5, "sources": []},
            "blockchain": {"source_count": 3, "sources": []},
            "cloud computing": {"source_count": 4, "sources": []}
        })
        
        self.processor.get_emerging_repositories = MagicMock(return_value=[
            {"name": "user/project1", "stars": 1000, "language": "Python"},
            {"name": "user/project2", "stars": 800, "language": "JavaScript"},
            {"name": "user/project3", "stars": 600, "language": "Rust"}
        ])
        
        self.processor.get_hot_discussions = MagicMock(return_value=[
            {"title": "Discussion 1", "source": "stackoverflow", "engagement_score": 100},
            {"title": "Discussion 2", "source": "reddit/r/programming", "engagement_score": 80},
            {"title": "Discussion 3", "source": "stackoverflow", "engagement_score": 60}
        ])
        
        self.processor.get_technology_correlations = MagicMock(return_value={
            "python": {"javascript": 0.5, "rust": 0.3},
            "javascript": {"python": 0.5, "rust": 0.4},
            "rust": {"python": 0.3, "javascript": 0.4}
        })
        
        # Call the method
        result = self.processor.get_technology_insights_report()
        
        # Assert results
        self.assertIsInstance(result, dict)
        
        # Check for expected fields
        self.assertIn("timestamp", result)
        self.assertIn("popularity_ranking", result)
        self.assertIn("trending_topics", result)
        self.assertIn("emerging_repositories", result)
        self.assertIn("hot_discussions", result)
        self.assertIn("tech_correlations", result)
        
        # Check for higher-level insights
        self.assertIn("top_technologies", result)
        self.assertIn("top_trending_topics", result)
        self.assertIn("top_emerging_repos", result)
        self.assertIn("top_discussions", result)
        
        # Check for technology clusters
        self.assertIn("technology_clusters", result)


if __name__ == '__main__':
    unittest.main()
