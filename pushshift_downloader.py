#!/usr/bin/env python3
"""
Pushshift dump downloader and processor
"""

import os
import gzip
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class PushshiftDownloader:
    """Download and process Pushshift Reddit dumps"""
    
    def __init__(self, data_dir: str = "pushshift_data"):
        """
        Initialize the downloader
        
        Args:
            data_dir: Directory to store downloaded dumps
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Pushshift dump URLs (these may need to be updated)
        self.base_url = "https://files.pushshift.io/reddit/submissions/"
        
        # Fields to keep for each post
        self.keep_fields = {
            "id", "created_utc", "title", "author", "num_comments", 
            "score", "permalink", "url", "selftext", "subreddit",
            "upvote_ratio", "over_18", "spoiler", "locked", "archived",
            "distinguished", "stickied", "is_self"
        }
    
    def get_available_months(self, months_back: int = 24) -> List[str]:
        """
        Get list of available month files to download
        
        Args:
            months_back: Number of months to look back
        
        Returns:
            List of month strings in format YYYY-MM
        """
        months = []
        current_date = datetime.now()
        
        for i in range(months_back):
            target_date = current_date - timedelta(days=30 * i)
            month_str = target_date.strftime("%Y-%m")
            months.append(month_str)
        
        return months
    
    def download_month_dump(self, month: str) -> str:
        """
        Download a month's dump file
        
        Args:
            month: Month in format YYYY-MM
        
        Returns:
            Path to downloaded file
        """
        # Try different file extensions
        extensions = [".zst", ".xz", ".gz"]
        filename = f"RS_{month}.json"
        
        for ext in extensions:
            url = f"{self.base_url}{filename}{ext}"
            local_path = self.data_dir / f"RS_{month}.json{ext}"
            
            if local_path.exists():
                logger.info(f"File already exists: {local_path}")
                return str(local_path)
            
            try:
                logger.info(f"Downloading {url}...")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Downloaded: {local_path}")
                return str(local_path)
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to download {url}: {e}")
                continue
        
        raise FileNotFoundError(f"Could not download dump for month {month}")
    
    def process_dump_file(self, file_path: str, target_subreddits: Set[str]) -> List[Dict]:
        """
        Process a dump file and extract posts from target subreddits
        
        Args:
            file_path: Path to the dump file
            target_subreddits: Set of subreddit names to extract
        
        Returns:
            List of filtered posts
        """
        posts = []
        file_path = Path(file_path)
        
        logger.info(f"Processing {file_path}...")
        
        # Determine compression type and open file
        if file_path.suffix == '.gz':
            open_func = gzip.open
            mode = 'rt'
        elif file_path.suffix == '.xz':
            import lzma
            open_func = lzma.open
            mode = 'rt'
        elif file_path.suffix == '.zst':
            # For .zst files, we'd need python-zstandard
            # For now, assume it's uncompressed
            open_func = open
            mode = 'rt'
        else:
            open_func = open
            mode = 'rt'
        
        try:
            with open_func(file_path, mode, encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 100000 == 0:
                        logger.info(f"Processed {line_num:,} lines...")
                    
                    try:
                        data = json.loads(line.strip())
                    except json.JSONDecodeError:
                        continue
                    
                    # Check if post is from target subreddit
                    subreddit = data.get("subreddit", "").lower()
                    if subreddit in target_subreddits:
                        # Filter to keep only self-posts
                        if data.get("is_self", False):
                            # Extract only the fields we want
                            filtered_post = {
                                k: data.get(k) for k in self.keep_fields
                            }
                            posts.append(filtered_post)
                    
                    # Stop if we have enough posts
                    if len(posts) >= 10000:  # Reasonable limit per month
                        break
                        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Extracted {len(posts)} posts from {file_path}")
        return posts
    
    def process_multiple_months(self, months: List[str], target_subreddits: Set[str]) -> Dict[str, List[Dict]]:
        """
        Process multiple month dumps
        
        Args:
            months: List of months to process
            target_subreddits: Set of subreddit names to extract
        
        Returns:
            Dictionary mapping months to lists of posts
        """
        all_posts = {}
        
        for month in months:
            try:
                # Download the dump
                dump_path = self.download_month_dump(month)
                
                # Process the dump
                posts = self.process_dump_file(dump_path, target_subreddits)
                all_posts[month] = posts
                
                # Add delay between downloads
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to process month {month}: {e}")
                all_posts[month] = []
        
        return all_posts
    
    def get_subreddit_posts(self, subreddit: str, months_back: int = 24, max_posts: int = 3000) -> List[Dict]:
        """
        Get posts for a specific subreddit from multiple months
        
        Args:
            subreddit: Subreddit name
            months_back: Number of months to look back
            max_posts: Maximum number of posts to return
        
        Returns:
            List of posts
        """
        target_subreddits = {subreddit.lower()}
        months = self.get_available_months(months_back)
        
        logger.info(f"Getting posts for r/{subreddit} from {len(months)} months")
        
        # Process all months
        monthly_posts = self.process_multiple_months(months, target_subreddits)
        
        # Combine all posts
        all_posts = []
        for month, posts in monthly_posts.items():
            all_posts.extend(posts)
        
        # Sort by creation time (newest first)
        all_posts.sort(key=lambda x: x.get('created_utc', 0), reverse=True)
        
        # Limit to max_posts
        final_posts = all_posts[:max_posts]
        
        logger.info(f"Retrieved {len(final_posts)} posts for r/{subreddit}")
        return final_posts


def main():
    """Example usage"""
    downloader = PushshiftDownloader()
    
    # Example: Get posts for a specific subreddit
    posts = downloader.get_subreddit_posts("antiwork", months_back=6, max_posts=1000)
    
    print(f"Retrieved {len(posts)} posts")
    if posts:
        print(f"First post: {posts[0]['title']}")


if __name__ == "__main__":
    main()

