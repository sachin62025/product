#!/usr/bin/env python3

import logging
import argparse
import json
import os
import sys
import pandas as pd
from tabulate import tabulate
import time

from data_processing.processor import DataProcessor
from utils.logger import setup_logger
from utils.cache import clear_cache, clear_expired_cache

# Initialize logger
logger = logging.getLogger(__name__)

def display_title():
    """Display the application title."""
    print(r"""                                                             
   Technology Trends Analyzer 
""")

def display_menu():
    """Display the main menu."""
    print("\nMAIN MENU")
    print("1. View Technology Popularity Rankings")
    print("2. Explore Trending Topics")
    print("3. Discover Emerging Repositories")
    print("4. Browse Hot Discussions")
    print("5. Analyze Technology Correlations")
    print("6. Generate Full Insights Report")
    print("7. Manage Cache")
    print("8. Exit")
    return input("\nSelect an option (1-8): ")

def display_table(data, title):
    """Display data in a tabular format."""
    print(f"\n{title}")
    print("="*80)
    print(tabulate(data, headers="keys", tablefmt="grid"))

def view_technology_popularity(processor):
    print("\nFetching technology popularity data...")
    popularity_data = processor.get_technology_popularity()
    
    # Convert to tabular format
    table_data = []
    for tech, data in list(popularity_data.items())[:20]:  # Show top 20
        table_data.append({
            "Technology": tech.capitalize(),
            "Overall Score": f"{data['overall_score']:.2f}",
            "GitHub Score": f"{data['platform_scores']['github']:.2f}",
            "Stack Overflow Score": f"{data['platform_scores']['stackoverflow']:.2f}",
            "Google Trends Score": f"{data['platform_scores']['pytrends']:.2f}"
        })
    
    display_table(table_data, "TECHNOLOGY POPULARITY RANKINGS (TOP 20)")

def explore_trending_topics(processor):

    print("\nFetching trending topics data...")
    topics_data = processor.get_trending_topics()
    
    if not topics_data:
        print("\nNo trending topics found.")
        return
    
    # Convert to tabular format
    table_data = []
    for topic, data in list(topics_data.items())[:15]:  # Show top 15
        sources_count = data['source_count']
        sources_text = ", ".join(set(source['source_type'] for source in data['sources'][:3]))
        if len(data['sources']) > 3:
            sources_text += "..."
        
        table_data.append({
            "Topic": topic,
            "Sources Count": sources_count,
            "Source Types": sources_text
        })
    
    display_table(table_data, "TRENDING TECHNOLOGY TOPICS")
    
    # Ask if user wants to see details for a specific topic
    topic_choice = input("\nEnter a topic number to see details (or press Enter to return): ")
    if topic_choice.isdigit() and 0 < int(topic_choice) <= len(table_data):
        topic_idx = int(topic_choice) - 1
        topic = list(topics_data.keys())[topic_idx]
        sources = topics_data[topic]['sources']
        
        print(f"\nDETAILS FOR TOPIC: {topic}")
        print("="*80)
        
        for i, source in enumerate(sources, 1):
            print(f"{i}. [{source['source_type'].upper()}] {source.get('title', 'No title')}")
            print(f"   URL: {source.get('url', 'No URL')}")
            
            # Add source-specific details
            if source['source_type'] == 'news':
                print(f"   Published: {source.get('published_at', 'Unknown')}")
            elif source['source_type'] == 'reddit':
                print(f"   Subreddit: r/{source.get('subreddit', 'Unknown')}")
            elif source['source_type'] == 'hackernews':
                print(f"   Score: {source.get('score', 'Unknown')}")
            
            print()

def discover_emerging_repositories(processor):

    print("\nFetching emerging repositories data...")
    repos_data = processor.get_emerging_repositories()
    
    if not repos_data:
        print("\nNo emerging repositories found.")
        return
    
    # Convert to tabular format
    table_data = []
    for i, repo in enumerate(repos_data[:15], 1):  # Show top 15
        table_data.append({
            "#": i,
            "Repository": repo['name'],
            "Description": (repo['description'][:50] + "...") if repo['description'] and len(repo['description']) > 50 else (repo['description'] or "No description"),
            "Language": repo['language'] or "Unknown",
            "Stars": repo['stars'],
            "Forks": repo['forks'],
            "Related Tech": repo.get('related_technology', 'Unknown')
        })
    
    display_table(table_data, "EMERGING GITHUB REPOSITORIES")
    
    # Ask if user wants to see details for a specific repository
    repo_choice = input("\nEnter a repository number to see details (or press Enter to return): ")
    if repo_choice.isdigit() and 0 < int(repo_choice) <= len(repos_data):
        repo_idx = int(repo_choice) - 1
        repo = repos_data[repo_idx]
        
        print(f"\nDETAILS FOR REPOSITORY: {repo['name']}")
        print("="*80)
        print(f"Description: {repo['description'] or 'No description'}")
        print(f"Language: {repo['language'] or 'Unknown'}")
        print(f"Stars: {repo['stars']}")
        print(f"Forks: {repo['forks']}")
        print(f"URL: {repo['url']}")
        print(f"Created at: {repo['created_at']}")
        
        if repo.get('topics'):
            print(f"Topics: {', '.join(repo['topics'])}")
        
        print(f"Related Technology: {repo.get('related_technology', 'Unknown')}")

def browse_hot_discussions(processor):

    print("\nFetching hot discussions data...")
    discussions_data = processor.get_hot_discussions()
    
    if not discussions_data:
        print("\nNo hot discussions found.")
        return
    
    # Convert to tabular format
    table_data = []
    for i, discussion in enumerate(discussions_data[:15], 1):  # Show top 15
        title = discussion['title']
        if len(title) > 60:
            title = title[:57] + "..."
            
        table_data.append({
            "#": i,
            "Title": title,
            "Source": discussion['source'],
            "Score": discussion.get('score', 'N/A'),
            "Comments": discussion.get('comment_count', discussion.get('answer_count', 'N/A')),
            "Technology": discussion.get('related_technology', 'Unknown')
        })
    
    display_table(table_data, "HOT TECHNOLOGY DISCUSSIONS")
    
    # Ask if user wants to see details for a specific discussion
    discussion_choice = input("\nEnter a discussion number to see details (or press Enter to return): ")
    if discussion_choice.isdigit() and 0 < int(discussion_choice) <= len(discussions_data):
        disc_idx = int(discussion_choice) - 1
        discussion = discussions_data[disc_idx]
        
        print(f"\nDETAILS FOR DISCUSSION: {discussion['title']}")
        print("="*80)
        print(f"Source: {discussion['source']}")
        print(f"URL: {discussion['url']}")
        
        if 'stackoverflow' in discussion['source']:
            print(f"Score: {discussion['score']}")
            print(f"Answer Count: {discussion['answer_count']}")
            print(f"View Count: {discussion['view_count']}")
        else:  # Reddit
            print(f"Score: {discussion['score']}")
            print(f"Comment Count: {discussion['comment_count']}")
        
        print(f"Related Technology: {discussion.get('related_technology', 'Unknown')}")

def analyze_technology_correlations(processor):

    print("\nFetching technology correlation data...")
    correlation_data = processor.get_technology_correlations()
    
    if not correlation_data:
        print("\nNo correlation data found.")
        return
    
    # Get the top technologies by number of correlations
    top_techs = []
    for tech, correlations in correlation_data.items():
        # Count significant correlations (> 0.3)
        significant_correlations = sum(1 for val in correlations.values() if val > 0.3)
        top_techs.append((tech, significant_correlations))
    
    # Sort by number of significant correlations
    top_techs.sort(key=lambda x: x[1], reverse=True)
    top_techs = top_techs[:10]  # Top 10
    
    print("\nTOP TECHNOLOGIES BY SIGNIFICANT CORRELATIONS")
    print("="*80)
    for i, (tech, count) in enumerate(top_techs, 1):
        print(f"{i}. {tech.capitalize()} - {count} significant correlations")
    
    # Ask if user wants to see correlations for a specific technology
    tech_choice = input("\nEnter a technology number to see its correlations (or press Enter to return): ")
    if tech_choice.isdigit() and 0 < int(tech_choice) <= len(top_techs):
        tech_idx = int(tech_choice) - 1
        tech = top_techs[tech_idx][0]
        
        # Get correlations for this technology
        techs_corr = correlation_data.get(tech, {})
        
        # Convert to tabular format
        table_data = []
        for other_tech, corr in sorted(techs_corr.items(), key=lambda x: x[1], reverse=True):
            if other_tech != tech and corr > 0.1:  # Only show non-trivial correlations
                table_data.append({
                    "Technology": other_tech.capitalize(),
                    "Correlation Strength": f"{corr:.3f}"
                })
        
        display_table(table_data, f"TECHNOLOGIES CORRELATED WITH {tech.upper()}")

def generate_insights_report(processor):

    print("\nGenerating comprehensive insights report...")
    print("This might take a while as we analyze data from multiple sources...")
    
    insights = processor.get_technology_insights_report()
    
    if not insights:
        print("\nFailed to generate insights report.")
        return
    
    print("\nTECHNOLOGY INSIGHTS REPORT")
    print("="*80)
    print(f"Report generated on: {insights['timestamp']}")
    
    # Show top technologies
    print("\nTOP TECHNOLOGIES BY OVERALL POPULARITY")
    print("-" * 50)
    for i, tech in enumerate(insights.get('top_technologies', []), 1):
        print(f"{i}. {tech['name'].capitalize()} (Score: {tech['score']:.2f})")
    
    # Show top trending topics
    print("\nTOP TRENDING TOPICS")
    print("-" * 50)
    for i, topic in enumerate(insights.get('top_trending_topics', []), 1):
        print(f"{i}. {topic['topic']} (Sources: {topic['source_count']})")
    
    # Show top emerging repositories
    print("\nTOP EMERGING REPOSITORIES")
    print("-" * 50)
    for i, repo in enumerate(insights.get('top_emerging_repos', []), 1):
        print(f"{i}. {repo['name']} - Stars: {repo['stars']}, Language: {repo['language'] or 'Unknown'}")
    
    # Show top discussions
    print("\nTOP HOT DISCUSSIONS")
    print("-" * 50)
    for i, disc in enumerate(insights.get('top_discussions', []), 1):
        print(f"{i}. {disc['title']}")
        print(f"   Source: {disc['source']}, Related to: {disc.get('related_technology', 'Unknown')}")
    
    # Show technology clusters
    print("\nTECHNOLOGY CLUSTERS")
    print("-" * 50)
    for i, cluster in enumerate(insights.get('technology_clusters', []), 1):
        print(f"{i}. {cluster['name']}")
        print(f"   Technologies: {', '.join(tech.capitalize() for tech in cluster['technologies'])}")
    
    # Ask if user wants to save the report
    save_choice = input("\nDo you want to save this report to a file? (y/n): ")
    if save_choice.lower() == 'y':
        filename = f"tech_insights_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(insights, f, indent=2)
            print(f"\nReport saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            print(f"\nError saving report: {e}")

def manage_cache():
    
    print("\nCACHE MANAGEMENT")
    print("1. Clear all cache")
    print("2. Clear expired cache only")
    print("3. Return to main menu")
    
    choice = input("\nSelect an option (1-3): ")
    
    if choice == '1':
        clear_cache()
        print("\nCache cleared successfully.")
    elif choice == '2':
        clear_expired_cache()
        print("\nExpired cache entries cleared successfully.")
    else:
        return

def cli_main():
    """Main function for the CLI interface."""
    setup_logger()
    
    # Initialize data processor
    processor = DataProcessor()
    
    display_title()
    print("Initializing data sources...")
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            view_technology_popularity(processor)
        elif choice == '2':
            explore_trending_topics(processor)
        elif choice == '3':
            discover_emerging_repositories(processor)
        elif choice == '4':
            browse_hot_discussions(processor)
        elif choice == '5':
            analyze_technology_correlations(processor)
        elif choice == '6':
            generate_insights_report(processor)
        elif choice == '7':
            manage_cache()
        elif choice == '8':
            print("\nThank you for using Data Alchemist. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    cli_main()
