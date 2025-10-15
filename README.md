# Reddit Post Scraper

A Python script to download Reddit posts from specified subreddits with time filtering and data processing capabilities.

## Features

- **Two Scraping Methods**:
  - **Pushshift Dumps** (Recommended): Fastest, most complete, no rate limits
  - **Reddit API**: Real-time data, requires authentication
- **Targeted Scraping**: Scrape 3,000 self-posts from each specified subreddit
- **Time Filtering**: Focus on posts from the last 24 months
- **Multiple Output Formats**: Save data as JSON and CSV files
- **Rate Limiting**: Respect Reddit API limits with built-in delays
- **Error Handling**: Robust error handling with retry mechanisms
- **Progress Tracking**: Real-time progress bars and logging
- **Data Processing**: Clean and filter posts based on criteria

## Why Use Pushshift Dumps?

- **Speed**: Orders of magnitude faster than API calls
- **Completeness**: Access to full historical data without gaps
- **No Rate Limits**: Process entire months of data without restrictions
- **Reliability**: No authentication or API downtime issues
- **Cost**: Completely free (vs potential API costs)
- **Bulk Processing**: Process multiple months simultaneously

## Supported Subreddits

The script is configured to scrape from these subreddits:

- r/antiwork
- r/raisedbynarcissists
- r/survivinginfidelity
- r/BreakUps
- r/depression
- r/Anxiety
- r/TrueOffMyChest
- r/offmychest
- r/RedditForGrownups
- r/selfimprovement
- r/AskReddit
- r/math

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd hai-raddit-crawler
   ```

2. **Run the setup script**:

   ```bash
   python setup.py
   ```

3. **Get Reddit API credentials**:

   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Note down your `client_id` and `client_secret`

4. **Configure credentials**:
   - Edit the `.env` file created by the setup script
   - Add your Reddit API credentials:
     ```
     REDDIT_CLIENT_ID=your_client_id_here
     REDDIT_CLIENT_SECRET=your_client_secret_here
     REDDIT_USER_AGENT=hai-reddit-crawler/1.0
     ```

## Usage

### Method 1: Pushshift Dumps (Recommended - Fastest & Most Complete)

This method uses Pushshift data dumps, which are orders of magnitude faster than API calls:

1. **Download Pushshift dumps**:

   ```bash
   # Download dumps from: https://files.pushshift.io/reddit/submissions/
   # Place them in the 'pushshift_data' directory
   ```

2. **Run the Pushshift scraper**:

   ```bash
   python main_pushshift.py
   ```

3. **Example filtering** (like your provided example):
   ```bash
   python example_pushshift.py
   ```

### Method 2: Reddit API (Slower but Real-time)

Run the API-based scraper:

```bash
python main.py
```

### Configuration

Edit `config.py` to modify scraping parameters:

- `POSTS_PER_SUBREDDIT`: Number of posts to scrape per subreddit (default: 3000)
- `MONTHS_BACK`: Time range in months (default: 24)
- `SUBREDDITS`: List of subreddits to scrape

### Output

The scraper creates several output files in the `data/` directory:

1. **Individual subreddit files**:

   - `{subreddit}_posts_{timestamp}.json`
   - `{subreddit}_posts_{timestamp}.csv`

2. **Combined data file**:

   - `all_subreddits_posts_{timestamp}.json`

3. **Summary report**:
   - `scraping_summary_{timestamp}.txt`

## Data Structure

Each post includes the following fields:

- `id`: Reddit post ID
- `title`: Post title
- `selftext`: Post content
- `author`: Post author
- `created_utc`: Creation timestamp
- `score`: Post score
- `upvote_ratio`: Upvote ratio
- `num_comments`: Number of comments
- `url`: Post URL
- `permalink`: Reddit permalink
- `subreddit`: Source subreddit
- `is_self`: Whether it's a self-post
- `over_18`: NSFW flag
- `spoiler`: Spoiler flag
- `locked`: Locked status
- `archived`: Archived status

## Rate Limiting

The script includes built-in rate limiting to respect Reddit's API limits:

- 1-second delay between requests
- 2-second delay between subreddits
- Exponential backoff on failures
- Random delays to avoid detection

## Error Handling

- Automatic retry on API failures
- Graceful handling of deleted/removed posts
- Comprehensive logging to `reddit_scraper.log`
- Progress tracking with detailed status updates

## Requirements

- Python 3.7+
- Reddit API credentials
- Internet connection

## Dependencies

- `praw`: Reddit API wrapper
- `pandas`: Data processing
- `python-dotenv`: Environment variable management
- `requests`: HTTP requests
- `tqdm`: Progress bars
- `python-dateutil`: Date utilities

## Troubleshooting

### Common Issues

1. **Authentication Error**:

   - Verify your Reddit API credentials in `.env`
   - Ensure your Reddit app is configured as "script" type

2. **Rate Limiting**:

   - The script includes rate limiting, but you may need to increase delays
   - Consider using Reddit username/password for higher limits

3. **No Posts Found**:

   - Some subreddits may have fewer posts than the target
   - Check if the subreddit exists and is accessible

4. **Permission Denied**:
   - Some subreddits may be private or restricted
   - The script will log these errors and continue

### Logs

Check `reddit_scraper.log` for detailed information about the scraping process.

## License

This project is for educational and research purposes. Please respect Reddit's Terms of Service and API usage guidelines.

## Contributing

Feel free to submit issues and enhancement requests!
