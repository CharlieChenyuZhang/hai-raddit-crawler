#!/usr/bin/env python3
"""
Example script showing how to use the Pushshift dump approach
"""

import gzip
import json
from pathlib import Path
from dump_processor import DumpProcessor


def simple_filter_example():
    """Simple example of filtering a dump file"""
    print("Simple Pushshift Dump Filtering Example")
    print("=" * 50)
    
    # Example: Filter a single dump file
    dump_file = Path("pushshift_data/RS_2024-01.json.gz")
    target_subreddits = {"antiwork", "depression", "anxiety"}
    output_file = Path("filtered_posts.jsonl")
    
    if not dump_file.exists():
        print(f"❌ Dump file not found: {dump_file}")
        print("You need to download Pushshift dumps first.")
        return
    
    processor = DumpProcessor()
    
    # Filter the dump
    posts_count = processor.filter_dump_by_subreddit(
        dump_file, target_subreddits, output_file, max_posts=1000
    )
    
    print(f"✅ Extracted {posts_count} posts to {output_file}")
    
    # Load and display some posts
    if output_file.exists():
        posts = processor.load_filtered_posts(output_file, max_posts=5)
        
        print(f"\nFirst {len(posts)} posts:")
        for i, post in enumerate(posts, 1):
            print(f"\n{i}. r/{post['subreddit']}")
            print(f"   Title: {post['title'][:80]}...")
            print(f"   Author: {post['author']}")
            print(f"   Score: {post['score']}")


def manual_filter_example():
    """Manual filtering example (like the one you provided)"""
    print("\nManual Filtering Example")
    print("=" * 30)
    
    # This is similar to your provided example
    sub = "antiwork"
    keep_fields = {
        "id", "created_utc", "title", "author", "num_comments", 
        "score", "permalink", "url", "selftext", "subreddit"
    }
    
    dump_file = Path("pushshift_data/RS_2024-01.json.gz")
    output_file = Path("manual_filtered.jsonl")
    
    if not dump_file.exists():
        print(f"❌ Dump file not found: {dump_file}")
        return
    
    posts_count = 0
    
    try:
        with gzip.open(dump_file, "rt", encoding="utf-8") as f, \
             open(output_file, "w", encoding="utf-8") as out:
            
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                if d.get("subreddit", "").lower() == sub:
                    # Filter to keep only self-posts
                    if d.get("is_self", False):
                        filtered_post = {k: d.get(k) for k in keep_fields}
                        out.write(json.dumps(filtered_post) + "\n")
                        posts_count += 1
                        
                        if posts_count >= 100:  # Limit for example
                            break
        
        print(f"✅ Manually filtered {posts_count} posts to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run examples"""
    print("Pushshift Dump Processing Examples")
    print("=" * 50)
    
    # Create directories
    Path("pushshift_data").mkdir(exist_ok=True)
    Path("filtered_data").mkdir(exist_ok=True)
    
    # Run examples
    simple_filter_example()
    manual_filter_example()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo get started with real data:")
    print("1. Download Pushshift dumps from: https://files.pushshift.io/reddit/submissions/")
    print("2. Place them in the 'pushshift_data' directory")
    print("3. Run: python main_pushshift.py")


if __name__ == "__main__":
    main()

