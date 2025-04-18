# Data Alchemist - Technology Trends Analyzer

Data Alchemist is a Python-based data aggregation and transformation tool that combines data from multiple public APIs to create meaningful insights about technology trends.

![Data Alchemist Dashboard](./screenshot.png)

## Overview

This project collects and analyzes data from 6 different public APIs to identify:

- Technology popularity rankings across different platforms
- Trending technology topics from news and social media
- Emerging GitHub repositories worth watching
- Hot discussions about technology
- Correlations between different technologies
- Technology clusters that are commonly used together

## Data Sources

Data Alchemist integrates with the following public APIs:

1. **GitHub API** - For repository and programming language statistics
2. **Stack Overflow API** - For popular questions and tag statistics
3. **HackerNews API** - For trending technology stories
4. **News API** - For technology news articles
5. **Reddit API** - For discussions from technology subreddits
6. **Google Trends** (via PyTrends) - For search volume trends

## Features

- **Comprehensive Data Collection**: Aggregates data from multiple authoritative sources
- **Advanced Analysis**: Identifies correlations, trends, and patterns across platforms
- **Dual Interface**: Both web-based and command-line interfaces
- **Visualizations**: Generates charts and visualizations of findings
- **Caching System**: Reduces API calls with a configurable caching mechanism
- **Modular Architecture**: Clean, modular code structure for maintainability
- **Robust Error Handling**: Gracefully handles API rate limits and failures



