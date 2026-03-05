import asyncio
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import aiohttp
from dateutil import parser as date_parser
import re
import json
import os


class DeepLearningRSSGenerator:
    def __init__(self):
        self.base_url = "https://www.deeplearning.ai/the-batch"
        self.rss_dir = "rss"
        self.rss_file = os.path.join(self.rss_dir, "deeplearning_the_batch_rss.xml")

    def parse_date(self, date_text):
        try:
            date_text = date_text.strip()
            parsed_date = date_parser.parse(date_text)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except Exception as e:
            print(f"Error parsing date '{date_text}': {e}")
            return datetime.now(timezone.utc)

    async def fetch_posts(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, headers=headers) as response:
                html_content = await response.text()
        
        articles_data = []
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html_content, re.DOTALL)
        
        if match:
            try:
                data = json.loads(match.group(1))
                posts = data.get('props', {}).get('pageProps', {}).get('posts', [])
                
                for post in posts:
                    title = post.get('title', '')
                    slug = post.get('slug', '')
                    published_at = post.get('published_at', '')
                    custom_excerpt = post.get('custom_excerpt', '')
                    
                    if not title or not slug:
                        continue
                    
                    full_url = f"https://www.deeplearning.ai/the-batch/{slug}/"
                    parsed_date = self.parse_date(published_at) if published_at else datetime.now(timezone.utc)
                    
                    articles_data.append({
                        'title': title,
                        'url': full_url,
                        'date': parsed_date,
                        'date_text': published_at,
                        'description': custom_excerpt
                    })
                    
                    print(f"Found: {title[:60]}... - {published_at[:10] if published_at else 'N/A'}")
                    
            except Exception as e:
                print(f"Error parsing JSON: {e}")
        
        articles_data.sort(key=lambda x: x['date'], reverse=True)
        
        return articles_data

    def create_feed(self):
        feed = FeedGenerator()
        feed.title('DeepLearning.AI The Batch')
        feed.link(href=self.base_url, rel='alternate')
        feed.description('Weekly AI News and Insights from DeepLearning.AI')
        feed.language('en')
        feed.link(href='https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/deeplearning_the_batch_rss.xml', rel='self')
        
        return feed

    def generate_rss(self, articles_data):
        feed = self.create_feed()
        
        for article_data in articles_data:
            entry = feed.add_entry()
            entry.title(article_data['title'])
            entry.link(href=article_data['url'])
            entry.pubDate(article_data['date'])
            entry.description(article_data.get('description', article_data['title']))
            entry.guid(article_data['url'], permalink=True)
            
        rss_content = feed.rss_str(pretty=True)
        return rss_content


async def main():
    generator = DeepLearningRSSGenerator()
    articles_data = await generator.fetch_posts()
    rss_content = generator.generate_rss(articles_data)
    
    os.makedirs(generator.rss_dir, exist_ok=True)
    
    with open(generator.rss_file, 'wb') as f:
        f.write(rss_content)
    
    print("RSS feed generated successfully!")


if __name__ == "__main__":
    asyncio.run(main())
