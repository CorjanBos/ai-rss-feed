import asyncio
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import aiohttp
from bs4 import BeautifulSoup
import re
from dateutil import parser as date_parser

class AnthropicRSSGenerator:
    def __init__(self):
        self.base_url = "https://www.anthropic.com/engineering"

    def parse_date(self, date_text):
        """Parse date text and return a datetime object with timezone"""
        try:
            # Clean up the date text
            date_text = date_text.strip()
            
            # Try to parse the date
            parsed_date = date_parser.parse(date_text)
            
            # If no timezone info, assume UTC
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            
            return parsed_date
        except Exception as e:
            print(f"Error parsing date '{date_text}': {e}")
            # Return current date as fallback with UTC timezone
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
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        articles_data = []
        articles = soup.select("article")
        
        for article in articles:
            try:
                title_element = article.select_one("h3")
                if not title_element:
                    continue
                title = title_element.get_text(strip=True)
                
                link_element = article.select_one("a")
                if not link_element:
                    continue
                url = link_element.get('href', '')
                if not url.startswith('http'):
                    url = f"https://www.anthropic.com{url}"
                
                date_element = article.select_one("div[class*='content'] > div, div[class*='date'], time")
                date_text = date_element.get_text(strip=True) if date_element else ""
                parsed_date = self.parse_date(date_text) if date_text else datetime.now(timezone.utc)
                
                articles_data.append({
                    'title': title,
                    'url': url,
                    'date': parsed_date,
                    'date_text': date_text
                })
                
                print(f"Found: {title} - {date_text}")
                
            except Exception as e:
                print(f"Error processing article: {e}")
        
        articles_data.sort(key=lambda x: x['date'], reverse=True)
        
        return articles_data

    def create_feed(self):
        """Create a fresh feed instance"""
        feed = FeedGenerator()
        feed.title('Anthropic Engineering Blog')
        feed.link(href=self.base_url, rel='alternate')
        feed.description('Latest engineering posts from Anthropic')
        feed.language('en')
        
        # Add atom:link with rel="self" for better interoperability
        # This should be updated to match your actual GitHub Pages URL
        feed.link(href='https://raw.githubusercontent.com/cnzhujie/anthropic-engineering-rss-feed/main/anthropic_engineering_rss.xml', rel='self')
        
        return feed

    def generate_rss(self, articles_data):
        # Create a fresh feed and add entries in sorted order
        feed = self.create_feed()
        
        for article_data in articles_data:
            entry = feed.add_entry()
            entry.title(article_data['title'])
            entry.link(href=article_data['url'])
            entry.pubDate(article_data['date'])
            entry.description(article_data['title'])
            
            # Add GUID for better interoperability (using the URL as GUID)
            entry.guid(article_data['url'], permalink=True)
            
        # Generate RSS feed content
        rss_content = feed.rss_str(pretty=True)
        return rss_content

async def main():
    generator = AnthropicRSSGenerator()
    articles_data = await generator.fetch_posts()
    rss_content = generator.generate_rss(articles_data)
    
    # Write to file
    with open('anthropic_engineering_rss.xml', 'wb') as f:
        f.write(rss_content)
    
    print("RSS feed generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
