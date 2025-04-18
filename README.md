# Data Alchemist - Technology Trends Analyzer

Data Alchemist is a Python-based data aggregation and transformation tool that combines data from multiple public APIs to create meaningful insights about technology trends.


![Screenshot 2025-04-16 171544](https://github.com/user-attachments/assets/91a16428-a59c-4a47-8778-50722b6879d8)
![Screenshot 2025-04-16 171640](https://github.com/user-attachments/assets/88d73003-df6f-4d49-9f69-7001b5f0f6ea)


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


Clone the repository

```bash
https://github.com/sachin62025/product.git
```
```bash
cd product
```
```bash
python main.py
```

## API Keys Configuration

To use the APIs in this project, add your respective API keys to a `.env` file in the root directory. The structure should look like this:

```plaintext
GITHUB_API_KEY=''
REDDIT_USERNAME=''
REDDIT_PASSWORD=''
REDDIT_CLIENT_ID=''
REDDIT_CLIENT_SECRET=''
STACKOVERFLOW_API_KEY=''
NEWS_API_KEY=''
