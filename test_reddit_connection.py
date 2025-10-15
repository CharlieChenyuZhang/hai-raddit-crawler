#!/usr/bin/env python3
"""
Test script to verify Reddit API connection
"""

import os
import praw
from dotenv import load_dotenv

def test_reddit_connection():
    """Test Reddit API connection"""
    
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'hai-reddit-crawler/1.0')
    
    print("Testing Reddit API connection...")
    print(f"Client ID: {'*' * 10 if client_id else 'Not set'}")
    print(f"Client Secret: {'*' * 10 if client_secret else 'Not set'}")
    print(f"User Agent: {user_agent}")
    print()
    
    if not client_id or not client_secret:
        print("❌ Missing Reddit API credentials!")
        print("Please run: python setup_credentials.py")
        return False
    
    try:
        # Initialize PRAW client
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test connection by accessing a public subreddit
        print("Testing connection to r/test...")
        subreddit = reddit.subreddit('test')
        display_name = subreddit.display_name
        print(f"✅ Successfully connected to r/{display_name}")
        
        # Try to get a few posts
        print("Testing post retrieval...")
        posts = list(subreddit.new(limit=3))
        print(f"✅ Successfully retrieved {len(posts)} posts")
        
        if posts:
            print("\nSample post:")
            post = posts[0]
            print(f"  Title: {post.title[:50]}...")
            print(f"  Author: {post.author}")
            print(f"  Score: {post.score}")
        
        print("\n🎉 Reddit API connection is working!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\nPossible issues:")
        print("1. Invalid Client ID or Client Secret")
        print("2. Incorrect User Agent format")
        print("3. Reddit API is down")
        print("4. Rate limiting")
        return False

if __name__ == "__main__":
    test_reddit_connection()
