"""
Configuration file for Reddit crawler
"""

# Subreddits to scrape
SUBREDDITS = [
    "antiwork",
    "raisedbynarcissists", 
    "survivinginfidelity",
    "BreakUps",
    "depression",
    "Anxiety",
    "TrueOffMyChest",
    "offmychest",
    "RedditForGrownups",
    "selfimprovement",
    "AskReddit",
    "math"
]

# Scraping parameters
POSTS_PER_SUBREDDIT = 3000
MONTHS_BACK = 24
OUTPUT_DIR = "data"
MAX_POSTS_PER_REQUEST = 100  # Reddit API limit

# File paths
ENV_FILE = ".env"

