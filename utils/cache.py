import os
import json
import pickle
import logging
import time
import functools
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure cache directory exists
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def cache_response(expires=3600):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function name and arguments
            key_parts = [func.__name__]
            
            # Add args to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    key_parts.append(str(arg))
                else:
                    try:
                        # For complex objects, use their string representation
                        key_parts.append(str(arg))
                    except:
                        # If that fails, use their type
                        key_parts.append(str(type(arg)))
            
            # Add kwargs to key (sorted for consistency)
            for k in sorted(kwargs.keys()):
                key_parts.append(f"{k}={kwargs[k]}")
            
            # Create a hash of the key parts to use as the cache key
            key_str = ':'.join(key_parts)
            cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Path for the cache file
            cache_path = os.path.join(CACHE_DIR, f"{cache_key}.cache")
            
            # Check if cache file exists and is still valid
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:
                        cache_time, cached_result = pickle.load(f)
                    
                    # Check if cache is still valid
                    if time.time() - cache_time < expires:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return cached_result
                    else:
                        logger.debug(f"Cache expired for {func.__name__}")
                except Exception as e:
                    logger.error(f"Error reading cache for {func.__name__}: {e}")
            
            # Cache miss or invalid, call the function
            result = func(*args, **kwargs)
            
            # Save the result to cache
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump((time.time(), result), f)
                logger.debug(f"Cached result for {func.__name__}")
            except Exception as e:
                logger.error(f"Error writing cache for {func.__name__}: {e}")
            
            return result
        return wrapper
    return decorator

def clear_cache():
   
    try:
        for file_path in Path(CACHE_DIR).glob('*.cache'):
            os.remove(file_path)
        logger.info("Cache cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")

def clear_expired_cache(max_age=86400):

    try:
        current_time = time.time()
        for file_path in Path(CACHE_DIR).glob('*.cache'):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age:
                os.remove(file_path)
        logger.info(f"Expired cache entries cleared (older than {max_age} seconds)")
    except Exception as e:
        logger.error(f"Error clearing expired cache: {e}")
