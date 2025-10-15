#!/usr/bin/env python3
"""
Main script for Reddit post scraping
"""

import os
import sys
import time
import logging
from typing import Dict, List
from tqdm import tqdm

from reddit_client import RedditClient
from data_processor import DataProcessor
from config import SUBREDDITS, POSTS_PER_SUBREDDIT, MONTHS_BACK, OUTPUT_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RedditScraper:
    """Main class for orchestrating Reddit post scraping"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.reddit_client = None
        self.data_processor = DataProcessor(OUTPUT_DIR)
        self.all_posts = {}
        
    def initialize(self) -> bool:
        """
        Initialize the Reddit client and test connection
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Reddit scraper...")
            self.reddit_client = RedditClient()
            
            if not self.reddit_client.test_connection():
                logger.error("Failed to connect to Reddit API")
                return False
            
            logger.info("Reddit scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit scraper: {e}")
            return False
    
    def scrape_subreddit(self, subreddit_name: str, max_posts: int = None) -> List[Dict]:
        """
        Scrape posts from a single subreddit
        
        Args:
            subreddit_name: Name of the subreddit to scrape
            max_posts: Maximum number of posts to scrape
        
        Returns:
            List of post dictionaries
        """
        if max_posts is None:
            max_posts = POSTS_PER_SUBREDDIT
        
        logger.info(f"Starting to scrape r/{subreddit_name} (target: {max_posts} posts)")
        
        try:
            posts = self.reddit_client.get_posts_by_timeframe(
                subreddit_name=subreddit_name,
                months_back=MONTHS_BACK,
                max_posts=max_posts
            )
            
            logger.info(f"Successfully scraped {len(posts)} posts from r/{subreddit_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping r/{subreddit_name}: {e}")
            return []
    
    def scrape_all_subreddits(self) -> Dict[str, List[Dict]]:
        """
        Scrape posts from all configured subreddits
        
        Returns:
            Dictionary mapping subreddit names to lists of posts
        """
        logger.info(f"Starting to scrape {len(SUBREDDITS)} subreddits")
        logger.info(f"Target: {POSTS_PER_SUBREDDIT} posts per subreddit")
        logger.info(f"Time range: Last {MONTHS_BACK} months")
        
        all_posts = {}
        
        # Create progress bar
        with tqdm(total=len(SUBREDDITS), desc="Scraping subreddits") as pbar:
            for subreddit in SUBREDDITS:
                pbar.set_description(f"Scraping r/{subreddit}")
                
                posts = self.scrape_subreddit(subreddit)
                all_posts[subreddit] = posts
                
                # Save individual subreddit data
                if posts:
                    self.data_processor.save_posts_to_json(posts, subreddit)
                    self.data_processor.save_posts_to_csv(posts, subreddit)
                
                pbar.update(1)
                
                # Add delay between subreddits to respect rate limits
                time.sleep(2)
        
        self.all_posts = all_posts
        return all_posts
    
    def save_results(self):
        """Save all scraping results"""
        if not self.all_posts:
            logger.warning("No posts to save")
            return
        
        logger.info("Saving scraping results...")
        
        # Save combined data
        self.data_processor.save_combined_data(self.all_posts)
        
        # Create summary report
        self.data_processor.create_summary_report(self.all_posts)
        
        logger.info("Results saved successfully")
    
    def print_summary(self):
        """Print a summary of the scraping results"""
        if not self.all_posts:
            logger.warning("No posts to summarize")
            return
        
        total_posts = sum(len(posts) for posts in self.all_posts.values())
        
        print("\n" + "="*60)
        print("REDDIT SCRAPING SUMMARY")
        print("="*60)
        print(f"Total subreddits scraped: {len(self.all_posts)}")
        print(f"Total posts collected: {total_posts}")
        print(f"Time range: Last {MONTHS_BACK} months")
        print(f"Output directory: {OUTPUT_DIR}")
        print("\nPer subreddit breakdown:")
        print("-" * 40)
        
        for subreddit, posts in self.all_posts.items():
            print(f"r/{subreddit:<20} {len(posts):>6} posts")
        
        print("="*60)
    
    def run(self):
        """Run the complete scraping process"""
        logger.info("Starting Reddit scraping process...")
        
        # Initialize
        if not self.initialize():
            logger.error("Failed to initialize scraper. Exiting.")
            return False
        
        # Scrape all subreddits
        self.scrape_all_subreddits()
        
        # Save results
        self.save_results()
        
        # Print summary
        self.print_summary()
        
        logger.info("Reddit scraping process completed successfully!")
        return True


def main():
    """Main function"""
    scraper = RedditScraper()
    success = scraper.run()
    
    if success:
        print("\n✅ Scraping completed successfully!")
        print(f"Check the '{OUTPUT_DIR}' directory for results.")
    else:
        print("\n❌ Scraping failed. Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

