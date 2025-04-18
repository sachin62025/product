"""
Google Trends API client using pytrends package to fetch search trend data.
"""
import logging
import time
import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from utils.cache import cache_response

logger = logging.getLogger(__name__)

class PyTrendsClient:
    """Client for Google Trends API to fetch search trend data."""
    
    def __init__(self):
        """Initialize the PyTrends client."""
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360)
        except Exception as e:
            logger.error(f"Error initializing PyTrends client: {e}")
            self.pytrends = None
    
    @cache_response(expires=6*3600)  # Cache for 6 hours
    def get_tech_trends(self, timeframe='today 3-m'):
        """
        Fetch trending technology-related search terms.
        
        Args:
            timeframe (str): Time frame for the data, e.g., 'today 3-m' for last 3 months
                            Other examples: 'now 1-d', 'now 7-d', 'today 1-m', 'today 12-m'
            
        Returns:
            dict: Dictionary with trending technology terms and their scores
        """
        if not self.pytrends:
            logger.error("PyTrends client not initialized. Cannot fetch trends.")
            return {}
        
        # List of technology keywords to explore
        tech_keywords = [
            'artificial intelligence', 'machine learning', 'programming language',
            'blockchain', 'cryptocurrency', 'cloud computing', 'data science',
            'web development', 'app development', 'cybersecurity'
        ]
        
        result = {}
        for keyword in tech_keywords:
            try:
                # Get related queries for each keyword
                self.pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
                related_queries = self.pytrends.related_queries()
                
                # Extract rising queries (trending terms)
                rising = related_queries.get(keyword, {}).get('rising')
                if isinstance(rising, pd.DataFrame) and not rising.empty:
                    # Convert to dictionary format
                    trend_dict = {}
                    for _, row in rising.iterrows():
                        term = row.get('query', '')
                        value = row.get('value', 0)
                        trend_dict[term] = value
                    
                    result[keyword] = trend_dict
                
                # Add a small delay to avoid hitting rate limits
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching trends for keyword '{keyword}': {e}")
                result[keyword] = {}
        
        return result
    
    @cache_response(expires=12*3600)  # Cache for 12 hours
    def compare_tech_terms(self, terms, timeframe='today 3-m'):
        """
        Compare interest over time for multiple technology terms.
        
        Args:
            terms (list): List of terms to compare (max 5 due to API limitations)
            timeframe (str): Time frame for the data
            
        Returns:
            dict: Dictionary with dates and relative interest scores for each term
        """
        if not self.pytrends:
            logger.error("PyTrends client not initialized. Cannot fetch comparison.")
            return {}
        
        # Ensure we don't exceed the limit of 5 terms
        if len(terms) > 5:
            logger.warning("PyTrends API limits comparisons to 5 terms. Truncating list.")
            terms = terms[:5]
        
        try:
            # Build payload with the terms to compare
            self.pytrends.build_payload(terms, cat=0, timeframe=timeframe, geo='', gprop='')
            
            # Get interest over time
            interest_over_time_df = self.pytrends.interest_over_time()
            
            # Convert DataFrame to dictionary
            result = {}
            if not interest_over_time_df.empty:
                for index, row in interest_over_time_df.iterrows():
                    date_str = index.strftime('%Y-%m-%d')
                    result[date_str] = {term: row[term] for term in terms if term in row}
            
            return result
            
        except Exception as e:
            logger.error(f"Error comparing tech terms: {e}")
            return {}
    
    @cache_response(expires=6*3600)
    def get_trending_technologies(self, top_n=10):
        """
        Get a curated list of trending technologies based on search popularity.
        
        Args:
            top_n (int): Number of trending technologies to return
            
        Returns:
            list: List of trending technologies with their relative popularity scores
        """
        if not self.pytrends:
            logger.error("PyTrends client not initialized. Cannot fetch trending technologies.")
            return []
        
        # Categories of technology to search for
        tech_categories = [
            'programming languages', 'web frameworks', 'databases',
            'cloud services', 'AI tools', 'mobile development'
        ]
        
        # Specific technologies to check
        technologies = {
            'programming languages': ['Python', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'Swift', 'Kotlin'],
            'web frameworks': ['React', 'Vue.js', 'Angular', 'Next.js', 'Svelte', 'Django', 'Flask'],
            'databases': ['MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Cassandra', 'DynamoDB'],
            'cloud services': ['AWS', 'Azure', 'Google Cloud', 'Cloudflare', 'Vercel', 'Netlify'],
            'AI tools': ['TensorFlow', 'PyTorch', 'OpenAI', 'GPT-4', 'DALL-E', 'Midjourney'],
            'mobile development': ['Flutter', 'React Native', 'SwiftUI', 'Jetpack Compose']
        }
        
        results = []
        
        # For each category, compare the technologies within that category
        for category, techs in technologies.items():
            # Process in batches of 5 due to API limitations
            for i in range(0, len(techs), 5):
                batch = techs[i:i+5]
                try:
                    self.pytrends.build_payload(batch, cat=0, timeframe='today 3-m', geo='', gprop='')
                    interest_df = self.pytrends.interest_over_time()
                    
                    if not interest_df.empty:
                        # Calculate average interest over the time period for each technology
                        for tech in batch:
                            if tech in interest_df.columns:
                                avg_interest = interest_df[tech].mean()
                                results.append({
                                    'name': tech,
                                    'category': category,
                                    'popularity': avg_interest
                                })
                    
                    # Add a small delay to avoid hitting rate limits
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error fetching interest for {category} - {batch}: {e}")
        
        # Sort by popularity and return top N
        results.sort(key=lambda x: x['popularity'], reverse=True)
        return results[:top_n]
