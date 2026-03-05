# RSS Feed Generator

This project generates RSS feeds for multiple AI-related blogs using HTTP requests and JSON parsing.

## Available Feeds

### Anthropic Engineering Blog
Feed URL: https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/anthropic_engineering_rss.xml

### DeepLearning.AI The Batch
Feed URL: https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/deeplearning_the_batch_rss.xml

### HuggingFace Blog
Feed URL: https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/huggingface_blog_rss.xml

### HuggingFace Trending Papers
Feed URL: https://raw.githubusercontent.com/cnzhujie/anthropic-engineering-rss-feed/main/huggingface_papers_rss.xml

### GitHub Trending Changes
Feed URL: https://raw.githubusercontent.com/cnzhujie/anthropic-engineering-rss-feed/main/github_trending_rss.xml

## Features

- **HTTP-based scraping**: Uses aiohttp for fast, lightweight HTTP requests
- **JSON data extraction**: Parses `__NEXT_DATA__` for client-side rendered content
- **Proper date parsing**: Extracts and formats publication dates with timezone support
- **RSS compliance**: Includes GUID elements and atom:link for better interoperability
- **Reverse chronological order**: Articles sorted newest first
- **Error handling**: Robust error handling for missing elements
- **Automated updates**: GitHub Action runs hourly to keep the feed current

## Setup

### Local Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the scripts:
```bash
# Generate Anthropic Engineering RSS
python anthropic_rss.py

# Generate DeepLearning.AI The Batch RSS
python deeplearning_rss.py

# Generate HuggingFace Blog RSS
python huggingface_rss.py

# Generate GitHub Trending RSS
python github_trending_rss.py
```

### GitHub Action Setup

1. Fork this repository to your GitHub account

2. Create a Personal Access Token (PAT):
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Click "Generate new token"
   - Name it "GitHub Actions RSS Updater"
   - Set repository access to your forked repository
   - Under "Repository permissions", grant:
     - Contents: Read and write
   - Click "Generate token" and copy the token

3. Add the token to your repository secrets:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `ANTHROPIC_RSS_GH_TOKEN`
   - Value: Paste the token you copied
   - Click "Add secret"

4. Update the RSS feed URLs in the scripts:
   - Replace the URLs with your GitHub username and repository name
   - Format: `https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/FILENAME.xml`

5. The GitHub Action will automatically:
   - Run every hour (and on push to main)
   - Generate fresh RSS feeds
   - Commit and push updates to the repository
   - Make the RSS feeds available at the raw GitHub URLs

### Accessing the RSS Feeds

Once set up, your RSS feeds will be available at:
```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/anthropic_engineering_rss.xml
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deeplearning_the_batch_rss.xml
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/huggingface_blog_rss.xml
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/huggingface_papers_rss.xml
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/github_trending_rss.xml
```

You can subscribe to these URLs in any RSS reader.

## Manual Triggering

You can manually trigger the RSS generation by:
- Going to the "Actions" tab in your GitHub repository
- Selecting "Generate Anthropic Engineering RSS Feed"
- Clicking "Run workflow"

## Output

The generated RSS feeds include:
- Post titles
- Post URLs  
- Publication dates (properly formatted)
- GUID elements for unique identification
- Descriptions (custom excerpts when available)
- Proper RSS metadata and atom:link elements

## Dependencies

- `aiohttp` - Async HTTP client
- `beautifulsoup4` - HTML parsing
- `feedgen` - RSS feed generation
- `python-dateutil` - Date parsing
