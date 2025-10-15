#!/usr/bin/env python3
"""
Example script showing how to use the Reddit scraper components
"""

import os
from reddit_client import RedditClient
from data_processor import DataProcessor
from utils import validate_reddit_credentials, format_timestamp


def example_single_subreddit():
    """Example: Scrape a single subreddit"""
    print("Example: Scraping a single subreddit")
    print("=" * 40)
    
    # Initialize client
    client = RedditClient()
    
    # Scrape a small number of posts from one subreddit
    posts = client.get_subreddit_posts("depression", limit=10)
    
    print(f"Retrieved {len(posts)} posts from r/depression")
    
    # Display first post
    if posts:
        post = posts[0]
        print(f"\nFirst post:")
        print(f"Title: {post['title']}")
        print(f"Author: {post['author']}")
        print(f"Created: {format_timestamp(post['created_utc'])}")
        print(f"Score: {post['score']}")
        print(f"Comments: {post['num_comments']}")
        print(f"Text preview: {post['selftext'][:100]}...")


def example_data_processing():
    """Example: Process and save data"""
    print("\nExample: Data processing")
    print("=" * 40)
    
    # Initialize processor
    processor = DataProcessor("example_data")
    
    # Get some sample data
    client = RedditClient()
    posts = client.get_subreddit_posts("anxiety", limit=5)
    
    if posts:
        # Save to JSON
        json_file = processor.save_posts_to_json(posts, "anxiety", "example_anxiety.json")
        print(f"Saved to JSON: {json_file}")
        
        # Save to CSV
        csv_file = processor.save_posts_to_csv(posts, "anxiety", "example_anxiety.csv")
        print(f"Saved to CSV: {csv_file}")
        
        # Create summary
        all_posts = {"anxiety": posts}
        summary_file = processor.create_summary_report(all_posts)
        print(f"Created summary: {summary_file}")


def example_filtering():
    """Example: Filter posts by criteria"""
    print("\nExample: Filtering posts")
    print("=" * 40)
    
    # Get posts
    client = RedditClient()
    posts = client.get_subreddit_posts("depression", limit=20)
    
    if posts:
        print(f"Original posts: {len(posts)}")
        
        # Filter by score
        high_score_posts = [p for p in posts if p['score'] > 10]
        print(f"Posts with score > 10: {len(high_score_posts)}")
        
        # Filter by comments
        commented_posts = [p for p in posts if p['num_comments'] > 5]
        print(f"Posts with > 5 comments: {len(commented_posts)}")
        
        # Filter by text length
        long_posts = [p for p in posts if len(p['selftext']) > 100]
        print(f"Posts with > 100 chars: {len(long_posts)}")


def main():
    """Run examples"""
    print("Reddit Scraper Examples")
    print("=" * 50)
    
    # Check if credentials are set
    if not validate_reddit_credentials(
        os.getenv('REDDIT_CLIENT_ID'),
        os.getenv('REDDIT_CLIENT_SECRET')
    ):
        print("❌ Reddit API credentials not found!")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file")
        return
    
    try:
        # Run examples
        example_single_subreddit()
        example_data_processing()
        example_filtering()
        
        print("\n✅ Examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    main()

