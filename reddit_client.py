"""
Reddit API client for scraping posts
"""

import os
import praw
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedditClient:
    """Reddit API client for scraping posts from subreddits"""
    
    def __init__(self):
        """Initialize Reddit client with API credentials"""
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'hai-reddit-crawler/1.0')
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_PASSWORD')
        
        # Initialize PRAW client - use read-only mode if no credentials
        if self.client_id and self.client_secret:
            # Authenticated mode
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                username=self.username,
                password=self.password
            )
            
            # Test connection
            try:
                self.reddit.user.me()
                logger.info("Successfully connected to Reddit API with authentication")
            except Exception as e:
                logger.warning(f"Could not authenticate as user: {e}")
                logger.info("Falling back to read-only mode")
                self._init_readonly_client()
        else:
            # Read-only mode (no authentication required)
            logger.info("No Reddit API credentials found. Using read-only mode.")
            self._init_readonly_client()
    
    def _init_readonly_client(self):
        """Initialize PRAW client in read-only mode"""
        self.reddit = praw.Reddit(
            client_id=None,
            client_secret=None,
            user_agent=self.user_agent
        )
    
    def get_subreddit_posts(
        self, 
        subreddit_name: str, 
        limit: int = 1000,
        time_filter: str = 'all',
        sort: str = 'new'
    ) -> List[Dict]:
        """
        Get posts from a specific subreddit
        
        Args:
            subreddit_name: Name of the subreddit (without r/)
            limit: Maximum number of posts to retrieve
            time_filter: Time filter ('all', 'year', 'month', 'week', 'day', 'hour')
            sort: Sort method ('new', 'hot', 'top', 'rising')
        
        Returns:
            List of post dictionaries
        """
        posts = []
        subreddit = self.reddit.subreddit(subreddit_name)
        
        try:
            logger.info(f"Fetching posts from r/{subreddit_name}")
            
            # Get posts based on sort method
            if sort == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort == 'top':
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == 'rising':
                submissions = subreddit.rising(limit=limit)
            else:
                submissions = subreddit.new(limit=limit)
            
            for submission in submissions:
                # Only include self posts (text posts)
                if submission.is_self:
                    post_data = self._extract_post_data(submission, subreddit_name)
                    posts.append(post_data)
                    
                    if len(posts) >= limit:
                        break
            
            logger.info(f"Retrieved {len(posts)} self posts from r/{subreddit_name}")
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
        
        return posts
    
    def get_posts_by_timeframe(
        self, 
        subreddit_name: str, 
        months_back: int = 24,
        max_posts: int = 3000
    ) -> List[Dict]:
        """
        Get posts from a subreddit within a specific timeframe
        
        Args:
            subreddit_name: Name of the subreddit
            months_back: Number of months to look back
            max_posts: Maximum number of posts to retrieve
        
        Returns:
            List of post dictionaries within the timeframe
        """
        posts = []
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        
        logger.info(f"Fetching posts from r/{subreddit_name} from the last {months_back} months")
        
        # Try different time filters to get posts from the specified timeframe
        time_filters = ['all', 'year', 'month']
        
        for time_filter in time_filters:
            if len(posts) >= max_posts:
                break
                
            remaining_posts = max_posts - len(posts)
            batch_posts = self.get_subreddit_posts(
                subreddit_name=subreddit_name,
                limit=remaining_posts,
                time_filter=time_filter,
                sort='new'
            )
            
            # Filter posts by date
            filtered_posts = [
                post for post in batch_posts 
                if post['created_utc'] >= cutoff_date.timestamp()
            ]
            
            posts.extend(filtered_posts)
            logger.info(f"Added {len(filtered_posts)} posts from {time_filter} filter")
            
            # Add delay to respect rate limits
            time.sleep(1)
        
        # Remove duplicates and sort by date
        unique_posts = self._remove_duplicates(posts)
        unique_posts.sort(key=lambda x: x['created_utc'], reverse=True)
        
        # Limit to max_posts
        final_posts = unique_posts[:max_posts]
        
        logger.info(f"Final count for r/{subreddit_name}: {len(final_posts)} posts")
        return final_posts
    
    def _extract_post_data(self, submission, subreddit_name: str) -> Dict:
        """Extract relevant data from a Reddit submission"""
        return {
            'id': submission.id,
            'title': submission.title,
            'selftext': submission.selftext,
            'author': str(submission.author) if submission.author else '[deleted]',
            'created_utc': submission.created_utc,
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'url': submission.url,
            'permalink': submission.permalink,
            'subreddit': subreddit_name,
            'is_self': submission.is_self,
            'over_18': submission.over_18,
            'spoiler': submission.spoiler,
            'locked': submission.locked,
            'archived': submission.archived,
            'distinguished': submission.distinguished,
            'stickied': submission.stickied
        }
    
    def _remove_duplicates(self, posts: List[Dict]) -> List[Dict]:
        """Remove duplicate posts based on ID"""
        seen_ids = set()
        unique_posts = []
        
        for post in posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)
        
        return unique_posts
    
    def test_connection(self) -> bool:
        """Test if the Reddit API connection is working"""
        try:
            # Try to access a public subreddit
            subreddit = self.reddit.subreddit('test')
            # Try to get the display name
            display_name = subreddit.display_name
            logger.info(f"Successfully connected to Reddit API (read-only mode)")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

