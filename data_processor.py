"""
Data processing and storage utilities for Reddit posts
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handle data processing and storage for Reddit posts"""
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize data processor
        
        Args:
            output_dir: Directory to store output files
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def save_posts_to_json(self, posts: List[Dict], subreddit_name: str, filename: Optional[str] = None) -> str:
        """
        Save posts to JSON file
        
        Args:
            posts: List of post dictionaries
            subreddit_name: Name of the subreddit
            filename: Optional custom filename
        
        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{subreddit_name}_posts_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Add metadata
        data = {
            'metadata': {
                'subreddit': subreddit_name,
                'total_posts': len(posts),
                'scraped_at': datetime.now().isoformat(),
                'date_range': self._get_date_range(posts)
            },
            'posts': posts
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(posts)} posts to {filepath}")
        return filepath
    
    def save_posts_to_csv(self, posts: List[Dict], subreddit_name: str, filename: Optional[str] = None) -> str:
        """
        Save posts to CSV file
        
        Args:
            posts: List of post dictionaries
            subreddit_name: Name of the subreddit
            filename: Optional custom filename
        
        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{subreddit_name}_posts_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to DataFrame
        df = pd.DataFrame(posts)
        
        # Add metadata as comments at the top
        metadata = f"# Subreddit: {subreddit_name}\n# Total posts: {len(posts)}\n# Scraped at: {datetime.now().isoformat()}\n# Date range: {self._get_date_range(posts)}\n"
        
        # Save with metadata
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata)
            df.to_csv(f, index=False)
        
        logger.info(f"Saved {len(posts)} posts to {filepath}")
        return filepath
    
    def save_combined_data(self, all_posts: Dict[str, List[Dict]], filename: Optional[str] = None) -> str:
        """
        Save all subreddit posts to a combined file
        
        Args:
            all_posts: Dictionary mapping subreddit names to lists of posts
            filename: Optional custom filename
        
        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_subreddits_posts_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Combine all posts with metadata
        combined_data = {
            'metadata': {
                'total_subreddits': len(all_posts),
                'scraped_at': datetime.now().isoformat(),
                'subreddit_stats': {}
            },
            'posts_by_subreddit': {}
        }
        
        total_posts = 0
        for subreddit, posts in all_posts.items():
            combined_data['posts_by_subreddit'][subreddit] = posts
            combined_data['metadata']['subreddit_stats'][subreddit] = {
                'post_count': len(posts),
                'date_range': self._get_date_range(posts)
            }
            total_posts += len(posts)
        
        combined_data['metadata']['total_posts'] = total_posts
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved combined data with {total_posts} posts from {len(all_posts)} subreddits to {filepath}")
        return filepath
    
    def create_summary_report(self, all_posts: Dict[str, List[Dict]]) -> str:
        """
        Create a summary report of the scraping results
        
        Args:
            all_posts: Dictionary mapping subreddit names to lists of posts
        
        Returns:
            Path to the summary report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraping_summary_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("REDDIT SCRAPING SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            total_posts = 0
            for subreddit, posts in all_posts.items():
                f.write(f"Subreddit: r/{subreddit}\n")
                f.write(f"  Posts collected: {len(posts)}\n")
                f.write(f"  Date range: {self._get_date_range(posts)}\n")
                f.write(f"  Average score: {self._get_average_score(posts):.2f}\n")
                f.write(f"  Average comments: {self._get_average_comments(posts):.2f}\n\n")
                total_posts += len(posts)
            
            f.write(f"TOTAL POSTS COLLECTED: {total_posts}\n")
            f.write(f"TOTAL SUBREDDITS: {len(all_posts)}\n")
        
        logger.info(f"Created summary report: {filepath}")
        return filepath
    
    def _get_date_range(self, posts: List[Dict]) -> str:
        """Get date range for a list of posts"""
        if not posts:
            return "No posts"
        
        timestamps = [post['created_utc'] for post in posts]
        earliest = datetime.fromtimestamp(min(timestamps))
        latest = datetime.fromtimestamp(max(timestamps))
        
        return f"{earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}"
    
    def _get_average_score(self, posts: List[Dict]) -> float:
        """Calculate average score for posts"""
        if not posts:
            return 0.0
        
        scores = [post['score'] for post in posts]
        return sum(scores) / len(scores)
    
    def _get_average_comments(self, posts: List[Dict]) -> float:
        """Calculate average number of comments for posts"""
        if not posts:
            return 0.0
        
        comments = [post['num_comments'] for post in posts]
        return sum(comments) / len(comments)
    
    def load_posts_from_json(self, filepath: str) -> Dict:
        """
        Load posts from JSON file
        
        Args:
            filepath: Path to the JSON file
        
        Returns:
            Dictionary containing posts and metadata
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {data['metadata']['total_posts']} posts from {filepath}")
        return data
    
    def filter_posts_by_criteria(self, posts: List[Dict], min_score: int = 0, min_comments: int = 0, min_text_length: int = 0) -> List[Dict]:
        """
        Filter posts based on specified criteria
        
        Args:
            posts: List of post dictionaries
            min_score: Minimum score threshold
            min_comments: Minimum number of comments
            min_text_length: Minimum text length
        
        Returns:
            Filtered list of posts
        """
        filtered_posts = []
        
        for post in posts:
            # Check score
            if post['score'] < min_score:
                continue
            
            # Check comments
            if post['num_comments'] < min_comments:
                continue
            
            # Check text length
            text_length = len(post['title']) + len(post['selftext'])
            if text_length < min_text_length:
                continue
            
            filtered_posts.append(post)
        
        logger.info(f"Filtered {len(posts)} posts down to {len(filtered_posts)} posts")
        return filtered_posts

