import os
import logging
import json

logger = logging.getLogger(__name__)

class Config:
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "api_timeout": 10,  # API request timeout in seconds
        "cache_expiry": {
            "github": 3600,        # 1 hour
            "stackoverflow": 3600, # 1 hour
            "hackernews": 1800,    # 30 minutes
            "news": 1800,          # 30 minutes
            "reddit": 1800,        # 30 minutes
            "pytrends": 6*3600     # 6 hours
        },
        "rate_limits": {
            "github": 60,          # 60 requests per hour for unauthenticated
            "stackoverflow": 300,  # 300 requests per day
            "hackernews": 500,     # No official limit, but be nice
            "news": 500,           # Depends on API key tier
            "reddit": 60,          # 60 requests per minute
            "pytrends": 1200       # Google can be restrictive, go slow
        }
    }
    
    def __init__(self):
       
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        
        # Load configuration from file if exists
        self.load_config()
    
    def load_config(self):
        """Load configuration from file if it exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    
                # Update configuration with file values
                for key, value in file_config.items():
                    if isinstance(value, dict) and key in self.config and isinstance(self.config[key], dict):
                        # Merge dictionaries for nested configurations
                        self.config[key].update(value)
                    else:
                        # Replace top-level configurations
                        self.config[key] = value
                        
                logger.info("Configuration loaded from file")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved to file")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key, default=None):

        if '.' in key:
            # Handle nested configuration (e.g., 'cache_expiry.github')
            parts = key.split('.')
            value = self.config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        else:
            # Handle top-level configuration
            return self.config.get(key, default)
    
    def set(self, key, value):

        if '.' in key:
            # Handle nested configuration
            parts = key.split('.')
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            # Handle top-level configuration
            self.config[key] = value
    
    def get_all(self):
        return self.config.copy()

# Create a singleton instance
config = Config()
