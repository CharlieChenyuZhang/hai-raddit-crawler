#!/usr/bin/env python3
"""
Efficient Pushshift dump processor
"""

import gzip
import json
import logging
from pathlib import Path
from typing import List, Dict, Set, Iterator
import time

logger = logging.getLogger(__name__)


class DumpProcessor:
    """Process Pushshift dump files efficiently"""
    
    def __init__(self):
        """Initialize the processor"""
        self.keep_fields = {
            "id", "created_utc", "title", "author", "num_comments", 
            "score", "permalink", "url", "selftext", "subreddit",
            "upvote_ratio", "over_18", "spoiler", "locked", "archived",
            "distinguished", "stickied", "is_self"
        }
    
    def open_dump_file(self, file_path: Path):
        """Open a dump file with appropriate decompression"""
        if file_path.suffix == '.gz':
            return gzip.open(file_path, 'rt', encoding='utf-8')
        elif file_path.suffix == '.xz':
            import lzma
            return lzma.open(file_path, 'rt', encoding='utf-8')
        elif file_path.suffix == '.zst':
            # For .zst files, we'd need python-zstandard
            # For now, assume it's uncompressed
            return open(file_path, 'rt', encoding='utf-8')
        else:
            return open(file_path, 'rt', encoding='utf-8')
    
    def filter_dump_by_subreddit(self, file_path: Path, target_subreddits: Set[str], 
                                output_path: Path, max_posts: int = None) -> int:
        """
        Filter a dump file by subreddit and save to output file
        
        Args:
            file_path: Path to input dump file
            target_subreddits: Set of subreddit names to filter for
            output_path: Path to save filtered posts
            max_posts: Maximum number of posts to extract
        
        Returns:
            Number of posts extracted
        """
        posts_extracted = 0
        target_subreddits_lower = {s.lower() for s in target_subreddits}
        
        logger.info(f"Filtering {file_path} for subreddits: {target_subreddits}")
        
        with self.open_dump_file(file_path) as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                if line_num % 100000 == 0:
                    logger.info(f"Processed {line_num:,} lines, extracted {posts_extracted} posts")
                
                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                
                # Check if post is from target subreddit
                subreddit = data.get("subreddit", "").lower()
                if subreddit in target_subreddits_lower:
                    # Filter to keep only self-posts
                    if data.get("is_self", False):
                        # Extract only the fields we want
                        filtered_post = {
                            k: data.get(k) for k in self.keep_fields
                        }
                        outfile.write(json.dumps(filtered_post) + '\n')
                        posts_extracted += 1
                        
                        # Stop if we have enough posts
                        if max_posts and posts_extracted >= max_posts:
                            break
            
        logger.info(f"Extracted {posts_extracted} posts from {file_path}")
        return posts_extracted
    
    def process_multiple_dumps(self, dump_files: List[Path], target_subreddits: Set[str], 
                              output_dir: Path, max_posts_per_file: int = None) -> Dict[str, int]:
        """
        Process multiple dump files
        
        Args:
            dump_files: List of dump file paths
            target_subreddits: Set of subreddit names to filter for
            output_dir: Directory to save filtered files
            max_posts_per_file: Maximum posts per file
        
        Returns:
            Dictionary mapping file names to number of posts extracted
        """
        output_dir.mkdir(exist_ok=True)
        results = {}
        
        for dump_file in dump_files:
            if not dump_file.exists():
                logger.warning(f"Dump file not found: {dump_file}")
                continue
            
            # Create output filename
            output_filename = f"filtered_{dump_file.stem}.jsonl"
            output_path = output_dir / output_filename
            
            try:
                posts_count = self.filter_dump_by_subreddit(
                    dump_file, target_subreddits, output_path, max_posts_per_file
                )
                results[dump_file.name] = posts_count
                
            except Exception as e:
                logger.error(f"Error processing {dump_file}: {e}")
                results[dump_file.name] = 0
        
        return results
    
    def combine_filtered_files(self, filtered_files: List[Path], output_path: Path, 
                              max_posts: int = None) -> int:
        """
        Combine multiple filtered files into one
        
        Args:
            filtered_files: List of filtered file paths
            output_path: Path to save combined file
            max_posts: Maximum number of posts to include
        
        Returns:
            Total number of posts combined
        """
        total_posts = 0
        
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for file_path in filtered_files:
                if not file_path.exists():
                    continue
                
                logger.info(f"Combining {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        if max_posts and total_posts >= max_posts:
                            break
                        
                        outfile.write(line)
                        total_posts += 1
                
                if max_posts and total_posts >= max_posts:
                    break
        
        logger.info(f"Combined {total_posts} posts into {output_path}")
        return total_posts
    
    def load_filtered_posts(self, file_path: Path, max_posts: int = None) -> List[Dict]:
        """
        Load posts from a filtered file
        
        Args:
            file_path: Path to filtered file
            max_posts: Maximum number of posts to load
        
        Returns:
            List of post dictionaries
        """
        posts = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if max_posts and len(posts) >= max_posts:
                    break
                
                try:
                    post = json.loads(line.strip())
                    posts.append(post)
                except json.JSONDecodeError:
                    continue
        
        logger.info(f"Loaded {len(posts)} posts from {file_path}")
        return posts
    
    def get_posts_by_subreddit(self, filtered_file: Path, subreddit: str, 
                              max_posts: int = None) -> List[Dict]:
        """
        Get posts for a specific subreddit from a filtered file
        
        Args:
            filtered_file: Path to filtered file
            subreddit: Subreddit name
            max_posts: Maximum number of posts to return
        
        Returns:
            List of posts for the subreddit
        """
        posts = []
        target_subreddit = subreddit.lower()
        
        with open(filtered_file, 'r', encoding='utf-8') as f:
            for line in f:
                if max_posts and len(posts) >= max_posts:
                    break
                
                try:
                    post = json.loads(line.strip())
                    if post.get('subreddit', '').lower() == target_subreddit:
                        posts.append(post)
                except json.JSONDecodeError:
                    continue
        
        logger.info(f"Found {len(posts)} posts for r/{subreddit}")
        return posts


def main():
    """Example usage"""
    processor = DumpProcessor()
    
    # Example: Process a single dump file
    dump_file = Path("pushshift_data/RS_2024-01.json.gz")
    target_subreddits = {"antiwork", "depression", "anxiety"}
    output_file = Path("filtered_posts.jsonl")
    
    if dump_file.exists():
        posts_count = processor.filter_dump_by_subreddit(
            dump_file, target_subreddits, output_file, max_posts=1000
        )
        print(f"Extracted {posts_count} posts")
    else:
        print(f"Dump file not found: {dump_file}")


if __name__ == "__main__":
    main()

