"""
Data processor module for aggregating and transforming data from multiple APIs.
"""
import logging
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime

from api_clients.github_client import GitHubClient
from api_clients.stackoverflow_client import StackOverflowClient
from api_clients.hackernews_client import HackerNewsClient
from api_clients.news_client import NewsClient
from api_clients.reddit_client import RedditClient
from api_clients.pytrends_client import PyTrendsClient

logger = logging.getLogger(__name__)

class DataProcessor:
    
    def __init__(self):
        """Initialize the data processor with API clients."""
        self.github_client = GitHubClient()
        self.stackoverflow_client = StackOverflowClient()
        self.hackernews_client = HackerNewsClient()
        self.news_client = NewsClient()
        self.reddit_client = RedditClient()
        self.pytrends_client = PyTrendsClient()
    
    def get_technology_popularity(self):
 
        logger.info("Analyzing technology popularity across platforms...")
        
        # Collect data from different sources
        github_languages = self.github_client.get_language_stats(limit=30)
        stackoverflow_tags = self.stackoverflow_client.get_popular_tags(limit=30)
        pytrends_tech = self.pytrends_client.get_trending_technologies(top_n=20)
        
        # Extract technology names and normalize
        technologies = set()
        
        # From GitHub languages
        for lang in github_languages.keys():
            technologies.add(lang.lower())
        
        # From Stack Overflow tags
        for tag in stackoverflow_tags:
            technologies.add(tag['name'].lower())
        
        # From PyTrends
        for tech in pytrends_tech:
            technologies.add(tech['name'].lower())
        
        # Create a standardized technology list
        tech_popularity = {}
        for tech in technologies:
            # Initialize scores for each platform
            scores = {
                'github': 0,
                'stackoverflow': 0,
                'pytrends': 0
            }
            
            # Calculate GitHub score (normalized)
            for lang, count in github_languages.items():
                if lang.lower() == tech:
                    max_count = max(github_languages.values()) if github_languages else 1
                    scores['github'] = (count / max_count) * 100
            
            # Calculate Stack Overflow score (normalized)
            for tag in stackoverflow_tags:
                if tag['name'].lower() == tech:
                    max_count = max(tag['count'] for tag in stackoverflow_tags) if stackoverflow_tags else 1
                    scores['stackoverflow'] = (tag['count'] / max_count) * 100
            
            # Calculate PyTrends score (normalized)
            for trend in pytrends_tech:
                if trend['name'].lower() == tech:
                    max_popularity = max(t['popularity'] for t in pytrends_tech) if pytrends_tech else 1
                    scores['pytrends'] = (trend['popularity'] / max_popularity) * 100
            
            # Calculate overall score (weighted average)
            weights = {'github': 0.4, 'stackoverflow': 0.4, 'pytrends': 0.2}
            overall_score = sum(score * weights[platform] for platform, score in scores.items())
            
            # Add to results if the technology has some presence
            if overall_score > 0:
                tech_popularity[tech] = {
                    'overall_score': overall_score,
                    'platform_scores': scores
                }
        
        # Sort by overall score and return top results
        sorted_tech = sorted(tech_popularity.items(), key=lambda x: x[1]['overall_score'], reverse=True)
        return dict(sorted_tech)
    
    def get_trending_topics(self):

        logger.info("Identifying trending topics...")
        
        # Collect data from different sources
        news_articles = self.news_client.get_tech_news(days=3, limit=20)
        reddit_posts = []
        for subreddit, posts in self.reddit_client.get_tech_subreddit_posts(limit=5).items():
            reddit_posts.extend(posts)
        hackernews_stories = self.hackernews_client.get_tech_stories(limit=20)
        
        # Extract titles and descriptions for text analysis
        texts = []
        
        # From news articles
        for article in news_articles:
            texts.append(article['title'])
            if article['description']:
                texts.append(article['description'])
        
        # From Reddit posts
        for post in reddit_posts:
            texts.append(post['title'])
        
        # From HackerNews stories
        for story in hackernews_stories:
            texts.append(story['title'])
        
        # Perform text analysis to identify key phrases and topics
        topics = self._extract_topics(texts)
        
        # Map topics back to their sources for context
        topic_sources = defaultdict(list)
        
        # Check each topic against each source
        for topic in topics:
            # Check news articles
            for article in news_articles:
                if topic.lower() in article['title'].lower() or (article['description'] and topic.lower() in article['description'].lower()):
                    topic_sources[topic].append({
                        'source_type': 'news',
                        'title': article['title'],
                        'url': article['url'],
                        'published_at': article['published_at']
                    })
            
            # Check Reddit posts
            for post in reddit_posts:
                if topic.lower() in post['title'].lower():
                    topic_sources[topic].append({
                        'source_type': 'reddit',
                        'title': post['title'],
                        'url': post['permalink'],
                        'subreddit': post['subreddit']
                    })
            
            # Check HackerNews stories
            for story in hackernews_stories:
                if topic.lower() in story['title'].lower():
                    topic_sources[topic].append({
                        'source_type': 'hackernews',
                        'title': story['title'],
                        'url': story['url'],
                        'score': story['score']
                    })
        
        # Format the results
        trending_topics = {}
        for topic, sources in topic_sources.items():
            # Only include topics with multiple sources
            if len(sources) >= 2:
                trending_topics[topic] = {
                    'sources': sources,
                    'source_count': len(sources)
                }
        
        # Sort by number of sources
        sorted_topics = sorted(trending_topics.items(), key=lambda x: x[1]['source_count'], reverse=True)
        return dict(sorted_topics)
    
    def get_emerging_repositories(self):

        logger.info("Identifying emerging repositories...")
        
        # Get trending technologies first
        trending_tech = list(self.get_technology_popularity().keys())[:15]
        
        # Get repositories for each trending technology
        emerging_repos = []
        for tech in trending_tech:
            # Try to find repositories related to this technology
            repos = self.github_client.get_trending_repositories(language=tech.capitalize(), since="weekly", limit=3)
            
            for repo in repos:
                # Add the technology as context
                repo['related_technology'] = tech
                emerging_repos.append(repo)
        
        # Sort by stars
        emerging_repos.sort(key=lambda x: x['stars'], reverse=True)
        return emerging_repos[:20]  # Return top 20
    
    def get_hot_discussions(self):

        logger.info("Finding hot discussions...")
        
        # Get trending technologies first
        trending_tech = list(self.get_technology_popularity().keys())[:10]
        
        # Get Stack Overflow questions related to trending technologies
        hot_discussions = []
        for tech in trending_tech:
            # Convert technology name to tag format (lowercase, no spaces)
            tag = tech.lower().replace(' ', '-')
            
            # Get questions from Stack Overflow
            questions = self.stackoverflow_client.get_popular_questions(tags=[tag], period="week", limit=2)
            
            for question in questions:
                hot_discussions.append({
                    'title': question['title'],
                    'url': question['link'],
                    'source': 'stackoverflow',
                    'score': question['score'],
                    'answer_count': question['answer_count'],
                    'view_count': question['view_count'],
                    'related_technology': tech
                })
        
        # Get Reddit discussions
        subreddits = ['programming', 'technology', 'webdev', 'MachineLearning']
        for subreddit in subreddits:
            posts = self.reddit_client.get_top_posts(subreddit=subreddit, time_filter="week", limit=5)
            
            for post in posts:
                # Check if post is related to any trending technology
                related_tech = None
                for tech in trending_tech:
                    if tech.lower() in post['title'].lower():
                        related_tech = tech
                        break
                
                if related_tech:
                    hot_discussions.append({
                        'title': post['title'],
                        'url': post['permalink'],
                        'source': f'reddit/r/{subreddit}',
                        'score': post['score'],
                        'comment_count': post['num_comments'],
                        'related_technology': related_tech
                    })
        
        # Sort by engagement metrics (normalized and combined score)
        for discussion in hot_discussions:
            if discussion['source'] == 'stackoverflow':
                discussion['engagement_score'] = (discussion['score'] * 2) + (discussion['answer_count'] * 5) + (discussion['view_count'] / 100)
            else:  # Reddit
                discussion['engagement_score'] = discussion['score'] + (discussion['comment_count'] * 5)
        
        hot_discussions.sort(key=lambda x: x['engagement_score'], reverse=True)
        return hot_discussions
    
    def get_technology_correlations(self):

        logger.info("Analyzing technology correlations...")
        
        # Get list of technologies to analyze
        trending_tech = list(self.get_technology_popularity().keys())[:20]
        
        # Get repositories and their associated technologies
        repositories = self.github_client.get_trending_repositories(limit=100)
        
        # Build co-occurrence matrix
        tech_pairs = []
        
        # Analyze repository topics and descriptions
        for repo in repositories:
            found_techs = []
            
            # Check description
            if repo['description']:
                for tech in trending_tech:
                    if tech.lower() in repo['description'].lower():
                        found_techs.append(tech)
            
            # Check topics
            for topic in repo['topics']:
                for tech in trending_tech:
                    if tech.lower() == topic.lower() or tech.lower() in topic.lower():
                        found_techs.append(tech)
            
            # Add all pairs of co-occurring technologies
            for i in range(len(found_techs)):
                for j in range(i+1, len(found_techs)):
                    tech_pairs.append((found_techs[i], found_techs[j]))
        
        # Get Stack Overflow questions and their tags
        for tech in trending_tech:
            questions = self.stackoverflow_client.get_popular_questions(tags=[tech.lower()], limit=20)
            
            for question in questions:
                found_techs = [tech]  # Start with the main technology
                
                # Check other tags
                for tag in question['tags']:
                    for other_tech in trending_tech:
                        if other_tech.lower() == tag.lower() and other_tech != tech:
                            found_techs.append(other_tech)
                
                # Add all pairs of co-occurring technologies
                for i in range(len(found_techs)):
                    for j in range(i+1, len(found_techs)):
                        tech_pairs.append((found_techs[i], found_techs[j]))
        
        # Count co-occurrences
        correlation_count = Counter(tech_pairs)
        
        # Calculate correlation matrix
        tech_count = Counter()
        for tech1, tech2 in tech_pairs:
            tech_count[tech1] += 1
            tech_count[tech2] += 1
        
        correlations = {}
        for (tech1, tech2), count in correlation_count.items():
            # Use Jaccard similarity: intersection / union
            similarity = count / (tech_count[tech1] + tech_count[tech2] - count)
            
            if tech1 not in correlations:
                correlations[tech1] = {}
            if tech2 not in correlations:
                correlations[tech2] = {}
            
            correlations[tech1][tech2] = similarity
            correlations[tech2][tech1] = similarity
        
        return correlations
    
    def get_technology_insights_report(self):

        logger.info("Generating comprehensive technology insights report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'popularity_ranking': self.get_technology_popularity(),
            'trending_topics': self.get_trending_topics(),
            'emerging_repositories': self.get_emerging_repositories(),
            'hot_discussions': self.get_hot_discussions(),
            'tech_correlations': self.get_technology_correlations()
        }
        
        # Add some higher-level insights
        
        # Top 10 technologies by overall popularity
        top_tech = sorted(report['popularity_ranking'].items(), 
                          key=lambda x: x[1]['overall_score'], reverse=True)[:10]
        report['top_technologies'] = [{'name': tech, 'score': data['overall_score']} 
                                      for tech, data in top_tech]
        
        # Top 5 trending topics by source count
        top_topics = sorted(report['trending_topics'].items(), 
                            key=lambda x: x[1]['source_count'], reverse=True)[:5]
        report['top_trending_topics'] = [{'topic': topic, 'source_count': data['source_count']} 
                                         for topic, data in top_topics]
        
        # Top 5 emerging repositories by stars
        report['top_emerging_repos'] = sorted(report['emerging_repositories'], 
                                              key=lambda x: x['stars'], reverse=True)[:5]
        
        # Top 5 hot discussions by engagement
        report['top_discussions'] = sorted(report['hot_discussions'], 
                                           key=lambda x: x['engagement_score'], reverse=True)[:5]
        
        # Find technology clusters based on correlations
        clusters = self._identify_technology_clusters(report['tech_correlations'])
        report['technology_clusters'] = clusters
        
        return report
    
    def _extract_topics(self, texts):

        # Define stop words (common words to ignore)
        stop_words = set([
            'the', 'and', 'is', 'of', 'to', 'a', 'in', 'for', 'on', 'with', 'as', 'by',
            'an', 'are', 'at', 'be', 'this', 'that', 'it', 'from', 'or', 'have', 'has',
            'new', 'more', 'how', 'what', 'why', 'when', 'who', 'where', 'which', 'not',
            'but', 'can', 'about', 'its', 'their', 'your', 'our', 'we', 'you', 'they',
            'now', 'get', 'all', 'one', 'two', 'three', 'over', 'may', 'just', 'first',
            'after', 'into', 'time', 'year', 'day', 'was', 'will', 'should', 'could',
            'would', 'do', 'if', 'my', 'than', 'then', 'no', 'only', 'also', 'use', 'using'
        ])
        
        # Define technology terms to specifically look for
        tech_terms = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network',
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'web3', 'nft',
            'cloud', 'aws', 'azure', 'google cloud', 'serverless', 'kubernetes', 'docker',
            'python', 'javascript', 'typescript', 'rust', 'go', 'java', 'c++', 'kotlin', 'swift',
            'react', 'vue', 'angular', 'svelte', 'next.js', 'django', 'flask', 'spring',
            'devops', 'cicd', 'security', 'cybersecurity', 'devsecops', 'encryption',
            'api', 'rest', 'graphql', 'microservices', 'serverless', 'edge computing',
            'quantum computing', 'augmented reality', 'virtual reality', 'ar', 'vr', 'metaverse',
            'data science', 'big data', 'analytics', 'visualization', 'business intelligence',
            'iot', 'internet of things', 'embedded', 'robotics', 'automation',
            '5g', '6g', 'networking', 'wifi', 'bluetooth', 'protocol', 'standard'
        ]
        
        # Process all texts
        word_counts = Counter()
        bigram_counts = Counter()
        trigram_counts = Counter()
        
        for text in texts:
            # Normalize text
            clean_text = text.lower()
            
            # Split into words
            words = clean_text.split()
            words = [word.strip('.,!?()[]{}:;"\'') for word in words]
            words = [word for word in words if word and word not in stop_words and len(word) > 2]
            
            # Count words
            word_counts.update(words)
            
            # Count bigrams (pairs of consecutive words)
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                bigram_counts[bigram] += 1
            
            # Count trigrams (triplets of consecutive words)
            for i in range(len(words) - 2):
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                trigram_counts[trigram] += 1
            
            # Check for specific tech terms
            for term in tech_terms:
                if term in clean_text:
                    word_counts[term] += 3  # Give higher weight to known tech terms
        
        # Combine all n-grams and sort by frequency
        all_phrases = []
        
        # Add most frequent words (excluding those that are part of frequent bigrams)
        for word, count in word_counts.most_common(100):
            # Skip words that are more valuable as part of bigrams
            skip = False
            for bigram in bigram_counts:
                if word in bigram.split() and bigram_counts[bigram] > count / 2:
                    skip = True
                    break
            
            if not skip:
                all_phrases.append((word, count))
        
        for bigram, count in bigram_counts.most_common(50):
            # Skip bigrams that are more valuable as part of trigrams
            skip = False
            for trigram in trigram_counts:
                if all(word in trigram.split() for word in bigram.split()) and trigram_counts[trigram] > count / 2:
                    skip = True
                    break
            
            if not skip:
                all_phrases.append((bigram, count * 1.5))  # Give higher weight to bigrams
        
        # Add most frequent trigrams
        for trigram, count in trigram_counts.most_common(30):
            all_phrases.append((trigram, count * 2))  # Give higher weight to trigrams
        
        # Sort by weight and return top phrases
        all_phrases.sort(key=lambda x: x[1], reverse=True)
        return [phrase for phrase, _ in all_phrases[:30]]  # Return top 30 topics
    
    def _identify_technology_clusters(self, correlations):
        """
        Identify clusters of related technologies based on correlation data.
        
        Args:
            correlations (dict): Dictionary with technology correlation data
            
        Returns:
            list: List of technology clusters
        """
        # Check if we have enough data
        if not correlations or len(correlations) < 3:
            return []
        
        # Convert correlation dict to a matrix format for easier processing
        technologies = list(correlations.keys())
        matrix = []
        
        for tech1 in technologies:
            row = []
            for tech2 in technologies:
                if tech2 in correlations.get(tech1, {}):
                    row.append(correlations[tech1][tech2])
                else:
                    row.append(0)
            matrix.append(row)
        
        # Convert to numpy array for better processing
        corr_matrix = np.array(matrix)
        
        # Simple clustering algorithm (hierarchical)
        clusters = []
        remaining_techs = set(technologies)
        
        # Threshold for considering technologies related
        threshold = 0.3
        
        while remaining_techs:
            # Start a new cluster with the first remaining technology
            current_tech = next(iter(remaining_techs))
            current_cluster = [current_tech]
            remaining_techs.remove(current_tech)
            
            # Find all technologies that correlate with the current technology
            tech_index = technologies.index(current_tech)
            for i, corr in enumerate(corr_matrix[tech_index]):
                if i != tech_index and technologies[i] in remaining_techs and corr > threshold:
                    current_cluster.append(technologies[i])
                    remaining_techs.remove(technologies[i])
            
            # Add the cluster if it has at least one technology
            if current_cluster:
                clusters.append(current_cluster)
        
        # Sort clusters by size
        clusters.sort(key=len, reverse=True)
        
        # Format the clusters with descriptive names
        named_clusters = []
        for i, cluster in enumerate(clusters):
            # Skip singleton clusters
            if len(cluster) < 2:
                continue
                
            # Try to determine a name for the cluster based on the technologies
            cluster_name = self._determine_cluster_name(cluster)
            
            named_clusters.append({
                'name': cluster_name,
                'technologies': cluster
            })
        
        return named_clusters
    
    def _determine_cluster_name(self, technologies):

        # Common technology categories for naming clusters
        categories = {
            'web development': ['javascript', 'typescript', 'react', 'vue', 'angular', 'html', 'css', 'node', 'webpack', 'bootstrap'],
            'data science': ['python', 'r', 'pandas', 'numpy', 'jupyter', 'data science', 'machine learning', 'analytics', 'visualization'],
            'ai & ml': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'tensorflow', 'pytorch', 'nlp'],
            'cloud & devops': ['cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'devops', 'ci/cd', 'terraform', 'serverless'],
            'mobile development': ['android', 'ios', 'swift', 'kotlin', 'flutter', 'react native', 'mobile'],
            'backend development': ['java', 'spring', 'django', 'flask', 'express', 'api', 'rest', 'graphql', 'microservices'],
            'database technologies': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'database', 'nosql'],
            'blockchain & crypto': ['blockchain', 'crypto', 'bitcoin', 'ethereum', 'web3', 'nft', 'defi', 'dao'],
            'systems programming': ['c', 'c++', 'rust', 'go', 'systems']
        }
        
        # Count matches for each category
        category_matches = {}
        for category, keywords in categories.items():
            matches = sum(any(tech.lower() in keyword.lower() or keyword.lower() in tech.lower() for tech in technologies) for keyword in keywords)
            category_matches[category] = matches
        
        # Find the category with the most matches
        best_category = max(category_matches.items(), key=lambda x: x[1])
        
        # Use the category name if it has at least 2 matches, otherwise use a generic name
        if best_category[1] >= 2:
            return best_category[0].title()
        else:
            return f"Related Technologies ({len(technologies)})"
