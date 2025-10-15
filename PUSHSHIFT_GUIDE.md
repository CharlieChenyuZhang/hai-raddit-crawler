# Pushshift Dumps Guide

## Overview

The Pushshift approach is **significantly better** than the Reddit API for your use case. Here's why and how to use it:

## Why Pushshift Dumps Are Superior

1. **Speed**: Orders of magnitude faster than API calls
2. **Completeness**: Access to full historical data without gaps
3. **No Rate Limits**: Process entire months without restrictions
4. **Reliability**: No authentication or API downtime issues
5. **Cost**: Completely free
6. **Bulk Processing**: Process multiple months simultaneously

## Quick Start

### 1. Download Pushshift Dumps

Visit: https://files.pushshift.io/reddit/submissions/

Download the files you need (e.g., `RS_2024-01.json.gz`, `RS_2024-02.json.gz`, etc.)

### 2. Place Files in Directory

```bash
mkdir pushshift_data
# Move downloaded files to pushshift_data/
```

### 3. Run the Scraper

```bash
python main_pushshift.py
```

## Manual Filtering (Like Your Example)

Here's the exact approach from your example, implemented in Python:

```python
import gzip, json

sub = "antiwork"
keep_fields = {"id","created_utc","title","author","num_comments","score","permalink","url","selftext"}

with gzip.open("RS_2025-06.zst.json.gz", "rt", encoding="utf-8") as f, \
     open("antiwork_2025-06.jsonl","w",encoding="utf-8") as out:
    for line in f:
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("subreddit","").lower() == sub:
            out.write(json.dumps({k:d.get(k) for k in keep_fields}) + "\n")
```

## File Structure

```
hai-raddit-crawler/
├── main_pushshift.py          # Main Pushshift scraper
├── pushshift_downloader.py    # Download and process dumps
├── dump_processor.py          # Efficient dump processing
├── example_pushshift.py       # Example usage
├── pushshift_data/            # Downloaded dump files
├── filtered_data/             # Filtered posts by month
└── data/                      # Final organized results
```

## Processing Flow

1. **Download**: Get Pushshift dump files
2. **Filter**: Extract posts from target subreddits
3. **Combine**: Merge filtered files
4. **Organize**: Group by subreddit
5. **Save**: Export to JSON/CSV formats

## Performance Comparison

| Method          | Speed      | Completeness | Rate Limits | Authentication |
| --------------- | ---------- | ------------ | ----------- | -------------- |
| Pushshift Dumps | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡⚡   | None        | None           |
| Reddit API      | ⚡⚡       | ⚡⚡⚡       | Strict      | Required       |

## Example Output

After processing, you'll get:

- `data/antiwork_posts_20241201_120000.json`
- `data/antiwork_posts_20241201_120000.csv`
- `data/all_subreddits_posts_20241201_120000.json`
- `data/scraping_summary_20241201_120000.txt`

## Troubleshooting

### Common Issues

1. **File Not Found**: Ensure dump files are in `pushshift_data/` directory
2. **Compression**: Some files use `.zst`, `.xz`, or `.gz` compression
3. **Memory**: Large dumps may require significant RAM

### File Extensions

- `.gz` - gzip compression
- `.xz` - xz compression
- `.zst` - zstandard compression
- No extension - uncompressed

## Next Steps

1. Download the Pushshift dumps you need
2. Run `python main_pushshift.py`
3. Check the `data/` directory for results

This approach will give you the complete, fast, and reliable data collection you need for your research!

