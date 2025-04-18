"""
Flask web application for the Data Alchemist project.
Provides a web interface for exploring technology trends.
"""
import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import json

from data_processing.processor import DataProcessor
from data_processing.analyzer import DataAnalyzer
from utils.logger import setup_logger
from utils.cache import clear_expired_cache

# Initialize logger
logger = logging.getLogger(__name__)
setup_logger(level=logging.DEBUG)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "data_alchemist_secret_key")

# Initialize data processor and analyzer
data_processor = DataProcessor()
data_analyzer = DataAnalyzer()

# Clear expired cache on startup
clear_expired_cache()

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/trends')
def trends():
    """Render the technology trends page."""
    return render_template('trends.html')

@app.route('/visualizations')
def visualizations():
    """Render the visualizations page."""
    return render_template('visualizations.html')

@app.route('/api/data/popularity')
def api_popularity():
    """API endpoint for technology popularity data."""
    try:
        popularity_data = data_processor.get_technology_popularity()
        return jsonify(popularity_data)
    except Exception as e:
        logger.error(f"Error in popularity API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/trending_topics')
def api_trending_topics():
    """API endpoint for trending topics data."""
    try:
        topics_data = data_processor.get_trending_topics()
        return jsonify(topics_data)
    except Exception as e:
        logger.error(f"Error in trending topics API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/emerging_repos')
def api_emerging_repos():
    """API endpoint for emerging repositories data."""
    try:
        repos_data = data_processor.get_emerging_repositories()
        return jsonify(repos_data)
    except Exception as e:
        logger.error(f"Error in emerging repositories API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/hot_discussions')
def api_hot_discussions():
    """API endpoint for hot discussions data."""
    try:
        discussions_data = data_processor.get_hot_discussions()
        return jsonify(discussions_data)
    except Exception as e:
        logger.error(f"Error in hot discussions API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/tech_correlations')
def api_tech_correlations():
    """API endpoint for technology correlation data."""
    try:
        correlation_data = data_processor.get_technology_correlations()
        return jsonify(correlation_data)
    except Exception as e:
        logger.error(f"Error in technology correlations API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/insights')
def api_insights():
    """API endpoint for comprehensive insights report."""
    try:
        insights_data = data_processor.get_technology_insights_report()
        return jsonify(insights_data)
    except Exception as e:
        logger.error(f"Error in insights API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api_viz_popularity')
def api_viz_popularity():
    """API endpoint for technology popularity visualization."""
    try:
        popularity_data = data_processor.get_technology_popularity()
        visualization = data_analyzer.create_technology_popularity_chart(popularity_data)
        return jsonify({"image": visualization})
    except Exception as e:
        logger.error(f"Error in popularity visualization API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api_viz_trending_topics')
def api_viz_trending_topics():
    """API endpoint for trending topics visualization."""
    try:
        topics_data = data_processor.get_trending_topics()
        visualization = data_analyzer.create_trending_topics_chart(topics_data)
        return jsonify({"image": visualization})
    except Exception as e:
        logger.error(f"Error in trending topics visualization API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api_viz_correlations')
def api_viz_correlations():
    """API endpoint for technology correlations visualization."""
    try:
        correlation_data = data_processor.get_technology_correlations()
        visualization = data_analyzer.create_tech_correlation_heatmap(correlation_data)
        return jsonify({"image": visualization})
    except Exception as e:
        logger.error(f"Error in correlations visualization API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api_viz_clusters')
def api_viz_clusters():
    """API endpoint for technology clusters visualization."""
    try:
        insights_data = data_processor.get_technology_insights_report()
        clusters = insights_data.get('technology_clusters', [])
        visualization = data_analyzer.create_technology_clusters_graph(clusters)
        return jsonify({"image": visualization})
    except Exception as e:
        logger.error(f"Error in clusters visualization API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api_viz_hot_discussions')
def api_viz_hot_discussions():
    """API endpoint for hot discussions visualization."""
    try:
        discussions_data = data_processor.get_hot_discussions()
        visualization = data_analyzer.create_hot_discussions_chart(discussions_data)
        return jsonify({"image": visualization})
    except Exception as e:
        logger.error(f"Error in hot discussions visualization API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api_viz_emerging_repos')
def api_viz_emerging_repos():
    try:
        repos_data = data_processor.get_emerging_repositories()
        visualization = data_analyzer.create_emerging_repos_chart(repos_data)
        return jsonify({"image": visualization})
    except Exception as e:
        logger.error(f"Error in emerging repositories visualization API: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
   
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
