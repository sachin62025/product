/**
 * Charts and data visualization utilities for Data Alchemist
 */

// Check if Chart is available before configuring
if (typeof Chart !== 'undefined') {
  // Chart theme setup (dark theme)
  Chart.defaults.color = '#fff';
  Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
  Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
}

/**
 * Creates a technology popularity chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Technology popularity data
 */
function createPopularityChart(elementId, data) {
    // Check if Chart is defined
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    const canvas = document.getElementById(elementId);
    if (!canvas) {
        console.error(`Canvas element with id '${elementId}' not found`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Process data for the chart
    const topTech = Object.entries(data)
        .sort((a, b) => b[1].overall_score - a[1].overall_score)
        .slice(0, 10);
    
    const labels = topTech.map(([tech, _]) => tech.charAt(0).toUpperCase() + tech.slice(1));
    const githubData = topTech.map(([_, scores]) => scores.platform_scores.github);
    const stackoverflowData = topTech.map(([_, scores]) => scores.platform_scores.stackoverflow);
    const pytrendsData = topTech.map(([_, scores]) => scores.platform_scores.pytrends);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'GitHub',
                    data: githubData,
                    backgroundColor: '#6e5494',
                    borderColor: '#6e5494',
                    borderWidth: 1
                },
                {
                    label: 'Stack Overflow',
                    data: stackoverflowData,
                    backgroundColor: '#f48024',
                    borderColor: '#f48024',
                    borderWidth: 1
                },
                {
                    label: 'Google Trends',
                    data: pytrendsData,
                    backgroundColor: '#fbbc05',
                    borderColor: '#fbbc05',
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Technology Popularity Across Platforms',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toFixed(1)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Score'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    stacked: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Creates a trending topics chart
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Trending topics data
 */
function createTrendingTopicsChart(elementId, data) {
    // Check if Chart is defined
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    const canvas = document.getElementById(elementId);
    if (!canvas) {
        console.error(`Canvas element with id '${elementId}' not found`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Process data for the chart
    const topTopics = Object.entries(data)
        .sort((a, b) => b[1].source_count - a[1].source_count)
        .slice(0, 8);
    
    const labels = topTopics.map(([topic, _]) => topic);
    const newsData = topTopics.map(([_, data]) => 
        data.sources.filter(s => s.source_type === 'news').length
    );
    const redditData = topTopics.map(([_, data]) => 
        data.sources.filter(s => s.source_type === 'reddit').length
    );
    const hackernewsData = topTopics.map(([_, data]) => 
        data.sources.filter(s => s.source_type === 'hackernews').length
    );
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'News',
                    data: newsData,
                    backgroundColor: '#007bff',
                    borderColor: '#007bff',
                    borderWidth: 1
                },
                {
                    label: 'Reddit',
                    data: redditData,
                    backgroundColor: '#ff4500',
                    borderColor: '#ff4500',
                    borderWidth: 1
                },
                {
                    label: 'HackerNews',
                    data: hackernewsData,
                    backgroundColor: '#ff6600',
                    borderColor: '#ff6600',
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Trending Topics by Source Mentions',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Number of Mentions'
                    }
                },
                y: {
                    stacked: true
                }
            }
        }
    });
}

/**
 * Creates a technology correlation heatmap
 * @param {string} elementId - The canvas element ID
 * @param {object} data - Technology correlation data
 */
function createCorrelationHeatmap(elementId, data) {
    // Check if Chart is defined
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    const canvas = document.getElementById(elementId);
    if (!canvas) {
        console.error(`Canvas element with id '${elementId}' not found`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Identify top technologies to include (those with the most correlations)
    const techCorrelationCounts = {};
    for (const tech in data) {
        techCorrelationCounts[tech] = Object.values(data[tech])
            .filter(val => val > 0.2)
            .length;
    }
    
    // Get top N technologies
    const topN = 10;
    const topTechs = Object.entries(techCorrelationCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, topN)
        .map(([tech, _]) => tech);
    
    // Create correlation matrix
    const matrix = [];
    for (const tech1 of topTechs) {
        const row = [];
        for (const tech2 of topTechs) {
            if (tech1 === tech2) {
                row.push(1.0); // Self-correlation is 1.0
            } else if (data[tech1] && data[tech1][tech2] !== undefined) {
                row.push(data[tech1][tech2]);
            } else {
                row.push(0);
            }
        }
        matrix.push(row);
    }
    
    // Labels with capitalized first letter
    const labels = topTechs.map(tech => tech.charAt(0).toUpperCase() + tech.slice(1));
    
    // Create the heatmap
    new Chart(ctx, {
        type: 'matrix',
        data: {
            datasets: [{
                label: 'Correlation Strength',
                data: matrix.flatMap((row, i) => 
                    row.map((value, j) => ({
                        x: j,
                        y: i,
                        v: value
                    }))
                ),
                backgroundColor(context) {
                    const value = context.dataset.data[context.dataIndex].v;
                    const alpha = Math.min(1, Math.max(0.1, value));
                    return `rgba(67, 160, 71, ${alpha})`;
                },
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1,
                width: ({ chart }) => (chart.chartArea || {}).width / topN - 1,
                height: ({ chart }) => (chart.chartArea || {}).height / topN - 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Technology Correlation Heatmap',
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title() {
                            return '';
                        },
                        label(context) {
                            const v = context.dataset.data[context.dataIndex];
                            return [
                                `${labels[v.y]} × ${labels[v.x]}`,
                                `Correlation: ${v.v.toFixed(2)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    labels: labels,
                    offset: true,
                    ticks: {
                        display: true
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'category',
                    labels: labels,
                    offset: true,
                    ticks: {
                        display: true
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Format date string for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
