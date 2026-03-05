import asyncio
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import aiohttp
from dateutil import parser as date_parser
import os


class HuggingFaceBlogRSSGenerator:
    def __init__(self):
        self.base_url = "https://huggingface.co/blog"
        self.api_url = "https://huggingface.co/api/blog"
        self.rss_dir = "rss"
        self.rss_file = os.path.join(self.rss_dir, "huggingface_blog_rss.xml")

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
            'Accept': 'application/json',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, headers=headers) as response:
                data = await response.json()
        
        articles_data = []
        all_blogs = data.get('allBlogs', [])
        
        for blog in all_blogs:
            try:
                title = blog.get('title', '')
                slug = blog.get('slug', '')
                published_at = blog.get('publishedAt', '')
                url_path = blog.get('url', '')
                
                authors_data = blog.get('authorsData', [])
                authors = []
                for author in authors_data:
                    author_name = author.get('fullname', '') or author.get('name', '')
                    if author_name:
                        authors.append(author_name)
                
                if not title or not slug:
                    continue
                
                if url_path:
                    full_url = f"https://huggingface.co{url_path}"
                else:
                    full_url = f"https://huggingface.co/blog/{slug}"
                
                parsed_date = self.parse_date(published_at) if published_at else datetime.now(timezone.utc)
                
                description = title
                if authors:
                    description = f"By {', '.join(authors)} - {title}"
                
                articles_data.append({
                    'title': title,
                    'url': full_url,
                    'date': parsed_date,
                    'date_text': published_at,
                    'description': description
                })
                
                print(f"Found: {title[:60]}... - {published_at[:10] if published_at else 'N/A'}")
                
            except Exception as e:
                print(f"Error processing blog: {e}")
        
        articles_data.sort(key=lambda x: x['date'], reverse=True)
        
        return articles_data

    def create_feed(self):
        feed = FeedGenerator()
        feed.title('HuggingFace Blog')
        feed.link(href=self.base_url, rel='alternate')
        feed.description('Latest posts from HuggingFace Blog')
        feed.language('en')
        feed.link(href='https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/huggingface_blog_rss.xml', rel='self')
        
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


class HuggingFacePapersRSSGenerator:
    def __init__(self):
        self.base_url = "https://huggingface.co/papers/trending"
        self.api_url = "https://huggingface.co/api/daily_papers"
        self.rss_dir = "rss"
        self.rss_file = os.path.join(self.rss_dir, "huggingface_papers_rss.xml")

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

    async def fetch_papers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, headers=headers) as response:
                data = await response.json()
        
        papers_data = []
        
        for item in data:
            try:
                paper = item.get('paper', {})
                
                paper_id = paper.get('id', '')
                title = paper.get('title', '')
                published_at = paper.get('publishedAt', '')
                summary = paper.get('summary', '')
                authors_list = paper.get('authors', [])
                
                if not paper_id or not title:
                    continue
                
                full_url = f"https://huggingface.co/papers/{paper_id}"
                
                authors = []
                for author in authors_list[:5]:
                    author_name = author.get('name', '')
                    if author_name:
                        authors.append(author_name)
                if len(authors_list) > 5:
                    authors.append(f"et al.")
                
                parsed_date = self.parse_date(published_at) if published_at else datetime.now(timezone.utc)
                
                description = title
                if authors:
                    description = f"By {', '.join(authors)}\n\n{summary[:300]}..." if summary else f"By {', '.join(authors)} - {title}"
                elif summary:
                    description = summary[:300] + "..."
                
                papers_data.append({
                    'title': title,
                    'url': full_url,
                    'date': parsed_date,
                    'date_text': published_at,
                    'description': description
                })
                
                print(f"Found: {title[:60]}... - {published_at[:10] if published_at else 'N/A'}")
                
            except Exception as e:
                print(f"Error processing paper: {e}")
        
        papers_data.sort(key=lambda x: x['date'], reverse=True)
        
        return papers_data

    def create_feed(self):
        feed = FeedGenerator()
        feed.title('HuggingFace Trending Papers')
        feed.link(href=self.base_url, rel='alternate')
        feed.description('Trending AI papers on HuggingFace')
        feed.language('en')
        feed.link(href='https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/huggingface_papers_rss.xml', rel='self')
        
        return feed

    def generate_rss(self, papers_data):
        feed = self.create_feed()
        
        for paper_data in papers_data:
            entry = feed.add_entry()
            entry.title(paper_data['title'])
            entry.link(href=paper_data['url'])
            entry.pubDate(paper_data['date'])
            entry.description(paper_data.get('description', paper_data['title']))
            entry.guid(paper_data['url'], permalink=True)
            
        rss_content = feed.rss_str(pretty=True)
        return rss_content


async def main():
    blog_generator = HuggingFaceBlogRSSGenerator()
    blog_data = await blog_generator.fetch_posts()
    blog_rss = blog_generator.generate_rss(blog_data)
    
    os.makedirs(blog_generator.rss_dir, exist_ok=True)
    
    with open(blog_generator.rss_file, 'wb') as f:
        f.write(blog_rss)
    
    print("\nHuggingFace Blog RSS feed generated successfully!")
    
    print("\nFetching trending papers...")
    papers_generator = HuggingFacePapersRSSGenerator()
    papers_data = await papers_generator.fetch_papers()
    papers_rss = papers_generator.generate_rss(papers_data)
    
    with open(papers_generator.rss_file, 'wb') as f:
        f.write(papers_rss)
    
    print("\nHuggingFace Papers RSS feed generated successfully!")


if __name__ == "__main__":
    asyncio.run(main())
