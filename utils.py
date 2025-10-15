"""
Utility functions for Reddit scraper
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def rate_limit(calls_per_minute: int = 60):
    """
    Decorator to rate limit function calls
    
    Args:
        calls_per_minute: Maximum number of calls per minute
    """
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]
        min_interval = 60.0 / calls_per_minute
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                logger.debug(f"Rate limiting: waiting {left_to_wait:.2f} seconds")
                time.sleep(left_to_wait)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    logger.info(f"Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    return decorator


def exponential_backoff(initial_delay: float = 1.0, max_delay: float = 60.0, multiplier: float = 2.0):
    """
    Decorator for exponential backoff on failures
    
    Args:
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Multiplier for delay after each failure
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Function {func.__name__} failed: {e}")
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    delay = min(delay * multiplier, max_delay)
            
            return None
        
        return wrapper
    return decorator


def random_delay(min_delay: float = 0.5, max_delay: float = 2.0):
    """
    Add random delay to avoid being detected as a bot
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_reddit_credentials(client_id: str, client_secret: str) -> bool:
    """
    Validate Reddit API credentials
    
    Args:
        client_id: Reddit client ID
        client_secret: Reddit client secret
    
    Returns:
        True if credentials are valid, False otherwise
    """
    if not client_id or not client_secret:
        logger.error("Missing Reddit API credentials")
        return False
    
    if len(client_id) < 10 or len(client_secret) < 10:
        logger.error("Reddit API credentials appear to be invalid (too short)")
        return False
    
    return True


def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to readable string
    
    Args:
        timestamp: Unix timestamp
    
    Returns:
        Formatted date string
    """
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def clean_text(text: str) -> str:
    """
    Clean text by removing unwanted characters and normalizing whitespace
    
    Args:
        text: Input text
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove common Reddit artifacts
    text = text.replace("[deleted]", "")
    text = text.replace("[removed]", "")
    
    return text.strip()


def is_valid_subreddit_name(name: str) -> bool:
    """
    Check if subreddit name is valid
    
    Args:
        name: Subreddit name
    
    Returns:
        True if valid, False otherwise
    """
    if not name:
        return False
    
    # Remove r/ prefix if present
    if name.startswith("r/"):
        name = name[2:]
    
    # Check length
    if len(name) < 1 or len(name) > 21:
        return False
    
    # Check characters (alphanumeric and underscores only)
    if not name.replace("_", "").isalnum():
        return False
    
    return True


def get_subreddit_display_name(name: str) -> str:
    """
    Get properly formatted subreddit display name
    
    Args:
        name: Subreddit name
    
    Returns:
        Formatted subreddit name with r/ prefix
    """
    if not name:
        return ""
    
    # Remove r/ prefix if present
    if name.startswith("r/"):
        name = name[2:]
    
    return f"r/{name}"


def estimate_scraping_time(num_subreddits: int, posts_per_subreddit: int) -> str:
    """
    Estimate total scraping time
    
    Args:
        num_subreddits: Number of subreddits to scrape
        posts_per_subreddit: Posts per subreddit
    
    Returns:
        Estimated time string
    """
    # Rough estimate: 1 second per post + 2 seconds per subreddit
    total_seconds = (posts_per_subreddit * num_subreddits) + (num_subreddits * 2)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

