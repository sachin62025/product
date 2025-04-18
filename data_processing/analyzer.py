"""
Data analyzer module for generating charts and visualizations.
"""
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.ticker import MaxNLocator
import seaborn as sns

logger = logging.getLogger(__name__)

class DataAnalyzer:

    def __init__(self):
        """Initialize the data analyzer."""
        # Set Matplotlib style for better visualizations
        plt.style.use('dark_background')
        
        # Common color scheme for consistent visualizations
        self.colors = {
            'primary': '#4582ec',
            'secondary': '#6f42c1',
            'success': '#02b875',
            'warning': '#f0ad4e',
            'danger': '#d9534f',
            'info': '#5bc0de',
            'github': '#6e5494',
            'stackoverflow': '#f48024',
            'hackernews': '#ff6600',
            'reddit': '#ff4500',
            'news': '#007bff',
            'pytrends': '#fbbc05'
        }
    
    def create_technology_popularity_chart(self, technology_data, top_n=10):

        # Get top N technologies by overall score
        top_tech = sorted(technology_data.items(), key=lambda x: x[1]['overall_score'], reverse=True)[:top_n]
        
        # Extract data for the chart
        tech_names = [tech.capitalize() for tech, _ in top_tech]
        overall_scores = [data['overall_score'] for _, data in top_tech]
        github_scores = [data['platform_scores']['github'] for _, data in top_tech]
        stackoverflow_scores = [data['platform_scores']['stackoverflow'] for _, data in top_tech]
        pytrends_scores = [data['platform_scores']['pytrends'] for _, data in top_tech]
        
        # Create the figure and axes
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create the stacked bar chart
        bar_width = 0.6
        indices = np.arange(len(tech_names))
        
        # Plot bars for each platform
        ax.bar(indices, github_scores, bar_width, label='GitHub', color=self.colors['github'], alpha=0.8)
        ax.bar(indices, stackoverflow_scores, bar_width, bottom=github_scores, label='Stack Overflow', color=self.colors['stackoverflow'], alpha=0.8)
        ax.bar(indices, pytrends_scores, bar_width, bottom=[g+s for g, s in zip(github_scores, stackoverflow_scores)], label='Google Trends', color=self.colors['pytrends'], alpha=0.8)
        
        # Customize the chart
        ax.set_title('Top Technologies by Popularity Across Platforms', fontsize=16)
        ax.set_ylabel('Normalized Score (0-100)', fontsize=12)
        ax.set_xlabel('Technology', fontsize=12)
        ax.set_xticks(indices)
        ax.set_xticklabels(tech_names, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add overall score as text above each bar
        for i, score in enumerate(overall_scores):
            ax.text(i, sum([github_scores[i], stackoverflow_scores[i], pytrends_scores[i]]) + 3, 
                    f'{score:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100)
        plt.close(fig)
        img.seek(0)
        
        # Encode the image to base64 string
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        return encoded
    
    def create_trending_topics_chart(self, topics_data, top_n=10):

        # Get top N topics by source count
        top_topics = sorted(topics_data.items(), key=lambda x: x[1]['source_count'], reverse=True)[:top_n]
        
        # Extract data for the chart
        topic_names = [topic for topic, _ in top_topics]
        source_counts = [data['source_count'] for _, data in top_topics]
        
        # Count sources by type for each topic
        news_counts = []
        reddit_counts = []
        hackernews_counts = []
        
        for _, data in top_topics:
            sources = data['sources']
            news_count = sum(1 for source in sources if source['source_type'] == 'news')
            reddit_count = sum(1 for source in sources if source['source_type'] == 'reddit')
            hackernews_count = sum(1 for source in sources if source['source_type'] == 'hackernews')
            
            news_counts.append(news_count)
            reddit_counts.append(reddit_count)
            hackernews_counts.append(hackernews_count)
        
        # Create the figure and axes
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create the horizontal stacked bar chart
        bar_height = 0.6
        indices = np.arange(len(topic_names))
        
        # Plot bars for each source type
        ax.barh(indices, news_counts, bar_height, label='News', color=self.colors['news'], alpha=0.8)
        ax.barh(indices, reddit_counts, bar_height, left=news_counts, label='Reddit', color=self.colors['reddit'], alpha=0.8)
        ax.barh(indices, hackernews_counts, bar_height, left=[n+r for n, r in zip(news_counts, reddit_counts)], label='HackerNews', color=self.colors['hackernews'], alpha=0.8)
        
        # Customize the chart
        ax.set_title('Trending Topics by Source Mentions', fontsize=16)
        ax.set_xlabel('Number of Sources', fontsize=12)
        ax.set_ylabel('Topic', fontsize=12)
        ax.set_yticks(indices)
        ax.set_yticklabels(topic_names)
        ax.legend(loc='lower right')
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Add total count as text next to each bar
        for i, count in enumerate(source_counts):
            ax.text(count + 0.1, i, f'{count}', va='center', fontsize=10, fontweight='bold')
        
        # Set integer ticks on x-axis
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100)
        plt.close(fig)
        img.seek(0)
        
        # Encode the image to base64 string
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        return encoded
    
    def create_tech_correlation_heatmap(self, correlation_data, top_n=15):

        # Identify top technologies to include (those with the most correlations)
        tech_correlation_counts = {}
        for tech, correlations in correlation_data.items():
            tech_correlation_counts[tech] = sum(1 for val in correlations.values() if val > 0.2)
        
        top_techs = sorted(tech_correlation_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_tech_names = [tech.capitalize() for tech, _ in top_techs]
        
        # Create correlation matrix for the selected technologies
        matrix_size = len(top_tech_names)
        corr_matrix = np.zeros((matrix_size, matrix_size))
        
        for i, tech1 in enumerate(top_tech_names):
            for j, tech2 in enumerate(top_tech_names):
                if i == j:  # Self-correlation is 1.0
                    corr_matrix[i, j] = 1.0
                else:
                    # Get correlation value from the data (case-insensitive)
                    tech1_lower = tech1.lower()
                    tech2_lower = tech2.lower()
                    if tech1_lower in correlation_data and tech2_lower in correlation_data[tech1_lower]:
                        corr_matrix[i, j] = correlation_data[tech1_lower][tech2_lower]
        
        # Create the figure and axes
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create the heatmap
        im = ax.imshow(corr_matrix, cmap='viridis')
        
        # Customize the chart
        ax.set_title('Technology Correlation Heatmap', fontsize=16)
        ax.set_xticks(np.arange(matrix_size))
        ax.set_yticks(np.arange(matrix_size))
        ax.set_xticklabels(top_tech_names, rotation=45, ha='right')
        ax.set_yticklabels(top_tech_names)
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Correlation Strength', rotation=270, labelpad=15)
        
        # Add correlation values as text in the cells
        for i in range(matrix_size):
            for j in range(matrix_size):
                if corr_matrix[i, j] > 0.3 or i == j:  # Only show stronger correlations
                    text_color = 'white' if corr_matrix[i, j] < 0.7 else 'black'
                    ax.text(j, i, f'{corr_matrix[i, j]:.2f}', ha='center', va='center', color=text_color, fontsize=9)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100)
        plt.close(fig)
        img.seek(0)
        
        # Encode the image to base64 string
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        return encoded
    
    def create_technology_clusters_graph(self, clusters_data):

        # Only proceed if we have clusters
        if not clusters_data:
            return None
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Colors for different clusters
        cluster_colors = [
            self.colors['primary'], self.colors['secondary'], self.colors['success'],
            self.colors['warning'], self.colors['danger'], self.colors['info'],
            '#e83e8c', '#20c997', '#17a2b8', '#6c757d', '#343a40'
        ]
        
        # Use NetworkX to layout the graph if available, otherwise use a manual approach
        try:
            import networkx as nx
            
            # Create a graph
            G = nx.Graph()
            
            # Add nodes for each technology
            all_techs = set()
            for cluster in clusters_data:
                for tech in cluster['technologies']:
                    all_techs.add(tech)
                    G.add_node(tech)
            
            # Add edges between technologies in the same cluster
            for cluster in clusters_data:
                techs = cluster['technologies']
                for i, tech1 in enumerate(techs):
                    for tech2 in techs[i+1:]:
                        G.add_edge(tech1, tech2)
            
            # Calculate layout
            pos = nx.spring_layout(G, k=0.15, iterations=50)
            
            # Draw the graph
            for i, cluster in enumerate(clusters_data):
                color = cluster_colors[i % len(cluster_colors)]
                nx.draw_networkx_nodes(G, pos, 
                                      nodelist=cluster['technologies'],
                                      node_color=color, 
                                      node_size=300,
                                      alpha=0.8,
                                      ax=ax)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=0.8, alpha=0.5, ax=ax)
            
            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=10, font_color='white', ax=ax)
            
            # Add cluster labels
            for i, cluster in enumerate(clusters_data):
                # Calculate the center position of the cluster
                cluster_techs = cluster['technologies']
                center_x = np.mean([pos[tech][0] for tech in cluster_techs])
                center_y = np.mean([pos[tech][1] for tech in cluster_techs])
                
                # Add a text label
                ax.text(center_x, center_y + 0.1, cluster['name'], 
                        fontsize=12, fontweight='bold', ha='center', 
                        bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.5'))
            
        except ImportError:
            # Manual approach if NetworkX is not available
            logger.warning("NetworkX not available. Using manual cluster visualization.")
            
            # Set up the plot
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            
            # Calculate positions for each cluster
            x_positions = np.linspace(1, 9, min(len(clusters_data), 5))
            y_positions = [7.5, 5, 2.5, 7.5, 5]  # Alternate rows for better spacing
            
            for i, cluster in enumerate(clusters_data[:5]):  # Limit to 5 clusters
                color = cluster_colors[i % len(cluster_colors)]
                x = x_positions[i % 5]
                y = y_positions[i % 5]
                
                # Draw cluster name
                ax.text(x, y + 1, cluster['name'], fontsize=12, fontweight='bold', 
                        ha='center', bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.5'))
                
                # Draw technologies in a circular arrangement
                techs = cluster['technologies'][:7]  # Limit to 7 technologies per cluster
                n_techs = len(techs)
                
                # Calculate positions in a circle
                radius = 0.8
                for j, tech in enumerate(techs):
                    angle = 2 * np.pi * j / n_techs
                    tech_x = x + radius * np.cos(angle)
                    tech_y = y + radius * np.sin(angle)
                    
                    # Draw technology node
                    ax.scatter(tech_x, tech_y, s=300, color=color, alpha=0.8, edgecolors='white')
                    
                    # Draw technology label
                    ax.text(tech_x, tech_y, tech.capitalize(), fontsize=9, ha='center', va='center')
        
        # Remove axes
        ax.axis('off')
        
        # Add title
        plt.title('Technology Clusters', fontsize=16)
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100)
        plt.close(fig)
        img.seek(0)
        
        # Encode the image to base64 string
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        return encoded
    
    def create_hot_discussions_chart(self, hot_discussions_data, top_n=10):

        top_discussions = sorted(hot_discussions_data, key=lambda x: x['engagement_score'], reverse=True)[:top_n]
        
        # Extract data for the chart
        titles = [f"{d['title'][:40]}..." if len(d['title']) > 40 else d['title'] for d in top_discussions]
        engagement_scores = [d['engagement_score'] for d in top_discussions]
        sources = [d['source'] for d in top_discussions]
        
        # Map sources to colors
        source_colors = []
        for source in sources:
            if 'stackoverflow' in source:
                source_colors.append(self.colors['stackoverflow'])
            elif 'reddit' in source:
                source_colors.append(self.colors['reddit'])
            else:
                source_colors.append(self.colors['hackernews'])
        
        # Create the figure and axes
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create the horizontal bar chart
        bars = ax.barh(range(len(titles)), engagement_scores, color=source_colors, alpha=0.8)
        
        # Customize the chart
        ax.set_title('Hottest Technology Discussions', fontsize=16)
        ax.set_xlabel('Engagement Score', fontsize=12)
        ax.set_yticks(range(len(titles)))
        ax.set_yticklabels(titles)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Add source labels to the right of each bar
        for i, (score, source) in enumerate(zip(engagement_scores, sources)):
            ax.text(score + max(engagement_scores) * 0.02, i, source, va='center', fontsize=9)
        
        # Create legend for sources
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['stackoverflow'], edgecolor='w', alpha=0.8, label='Stack Overflow'),
            Patch(facecolor=self.colors['reddit'], edgecolor='w', alpha=0.8, label='Reddit'),
            Patch(facecolor=self.colors['hackernews'], edgecolor='w', alpha=0.8, label='HackerNews')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100)
        plt.close(fig)
        img.seek(0)
        
        # Encode the image to base64 string
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        return encoded
    
    def create_emerging_repos_chart(self, repos_data, top_n=10):

        # Get top N repositories by stars
        top_repos = sorted(repos_data, key=lambda x: x['stars'], reverse=True)[:top_n]
        
        # Extract data for the chart
        names = [repo['name'].split('/')[-1] for repo in top_repos]  # Just the repo name, not owner
        stars = [repo['stars'] for repo in top_repos]
        forks = [repo['forks'] for repo in top_repos]
        languages = [repo['language'] if repo['language'] else 'Unknown' for repo in top_repos]
        
        # Map languages to colors (use a colormap for more variety)
        unique_languages = list(set(languages))
        language_colors = {}
        colormap = plt.cm.viridis(np.linspace(0, 1, len(unique_languages)))
        
        for i, lang in enumerate(unique_languages):
            language_colors[lang] = colormap[i]
        
        # Create the figure and axes
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create the scatter plot
        for i in range(len(top_repos)):
            ax.scatter(stars[i], forks[i], color=language_colors[languages[i]], 
                      s=100 + stars[i]/100, alpha=0.7, edgecolors='white')
            ax.text(stars[i] * 1.05, forks[i], names[i], fontsize=9)
        
        # Customize the chart
        ax.set_title('Emerging GitHub Repositories', fontsize=16)
        ax.set_xlabel('Stars', fontsize=12)
        ax.set_ylabel('Forks', fontsize=12)
        ax.grid(linestyle='--', alpha=0.7)
        
        # Use log scale for x-axis if the star counts vary widely
        if max(stars) / (min(stars) + 1) > 50:
            ax.set_xscale('log')
        
        # Create legend for languages
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=language_colors[lang], 
                  markersize=8, label=lang)
            for lang in unique_languages
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100)
        plt.close(fig)
        img.seek(0)
        
        # Encode the image to base64 string
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        return encoded
