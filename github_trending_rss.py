import asyncio
from datetime import datetime, timezone, timedelta
from feedgen.feed import FeedGenerator
import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import json
import os


class GitHubTrendingRSSGenerator:
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.data_dir = "github_trending_data"
        self.rss_dir = "rss"
        self.rss_file = os.path.join(self.rss_dir, "github_trending_rss.xml")

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

    def get_data_file_path(self, date=None):
        if date is None:
            date = datetime.now(timezone.utc)
        filename = f"{date.strftime('%Y-%m-%d')}.json"
        return os.path.join(self.data_dir, filename)

    def load_previous_data(self):
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        yesterday_file = self.get_data_file_path(yesterday)
        
        if os.path.exists(yesterday_file):
            try:
                with open(yesterday_file, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded previous data from {yesterday_file}")
                    return data
            except Exception as e:
                print(f"Error loading previous data: {e}")
        else:
            print(f"No previous data file found: {yesterday_file}")
        
        return {}

    def save_current_data(self, data):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            today_file = self.get_data_file_path()
            
            if os.path.exists(today_file):
                with open(today_file, 'r') as f:
                    existing_data = json.load(f)
                existing_data.update(data)
                data = existing_data
            
            with open(today_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Saved current data to {today_file}")
        except Exception as e:
            print(f"Error saving current data: {e}")

    async def fetch_trending(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, headers=headers) as response:
                html_content = await response.text()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        repos = []
        articles = soup.select('article.Box-row')
        
        for rank, article in enumerate(articles, 1):
            try:
                h2 = article.select_one('h2 a')
                if not h2:
                    continue
                
                repo_path = h2.get('href', '').strip('/')
                repo_name = repo_path.replace('/', ' / ')
                repo_url = f"https://github.com/{repo_path}"
                
                desc_p = article.select_one('p')
                description = desc_p.get_text(strip=True) if desc_p else ""
                
                stars_span = article.select_one('a[href$="/stargazers"]')
                stars_text = stars_span.get_text(strip=True) if stars_span else "0"
                stars = self.parse_stars(stars_text)
                
                forks_span = article.select_one('a[href$="/forks"]')
                forks_text = forks_span.get_text(strip=True) if forks_span else "0"
                forks = self.parse_stars(forks_text)
                
                language_span = article.select_one('span[itemprop="programmingLanguage"]')
                language = language_span.get_text(strip=True) if language_span else ""
                
                today_stars_span = article.select_one('span.float-sm-right')
                today_stars = today_stars_span.get_text(strip=True) if today_stars_span else ""
                
                repos.append({
                    'repo_path': repo_path,
                    'repo_name': repo_name,
                    'repo_url': repo_url,
                    'description': description,
                    'stars': stars,
                    'stars_text': stars_text,
                    'forks': forks,
                    'language': language,
                    'today_stars': today_stars,
                    'rank': rank,
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                })
                
                print(f"Found #{rank}: {repo_name} - {stars_text} stars")
                
            except Exception as e:
                print(f"Error processing repo: {e}")
        
        return repos

    def parse_stars(self, text):
        try:
            text = text.strip().replace(',', '')
            if 'k' in text.lower():
                return int(float(text.lower().replace('k', '')) * 1000)
            return int(text)
        except:
            return 0

    def compare_and_generate_updates(self, current_repos, previous_data):
        updates = []
        current_data = {}
        
        for repo in current_repos:
            repo_path = repo['repo_path']
            current_data[repo_path] = repo
            
            prev_repo = previous_data.get(repo_path)
            
            if prev_repo is None:
                change_info = f"🆕 NEW ENTRY - Ranked #{repo['rank']}"
                updates.append({
                    'repo': repo,
                    'change_info': change_info,
                    'is_new': True
                })
                print(f"  NEW: {repo['repo_name']} entered at #{repo['rank']}")
            else:
                changes = []
                has_change = False
                
                prev_rank = prev_repo.get('rank', 0)
                rank_change = prev_rank - repo['rank']
                if rank_change > 0:
                    changes.append(f"📈 Rank: #{prev_rank} → #{repo['rank']} (↑{rank_change})")
                    has_change = True
                elif rank_change < 0:
                    changes.append(f"📉 Rank: #{prev_rank} → #{repo['rank']} (↓{abs(rank_change)})")
                    has_change = True
                
                prev_stars = prev_repo.get('stars', 0)
                stars_change = repo['stars'] - prev_stars
                if stars_change > 0:
                    changes.append(f"⭐ Stars: {prev_repo.get('stars_text', '0')} → {repo['stars_text']} (+{stars_change})")
                    has_change = True
                elif stars_change < 0:
                    changes.append(f"⭐ Stars: {prev_repo.get('stars_text', '0')} → {repo['stars_text']} ({stars_change})")
                    has_change = True
                
                if rank_change == 0 and stars_change != 0:
                    changes.append(f"Ranked #{repo['rank']}")
                
                if has_change and changes:
                    change_info = " | ".join(changes)
                    updates.append({
                        'repo': repo,
                        'change_info': change_info,
                        'is_new': False
                    })
        
        return updates, current_data

    def create_feed(self):
        feed = FeedGenerator()
        feed.title('GitHub Trending Changes')
        feed.link(href=self.base_url, rel='alternate')
        feed.description('Track changes in GitHub trending repositories')
        feed.language('en')
        feed.link(href='https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/github_trending_rss.xml', rel='self')
        
        return feed

    def generate_rss(self, updates):
        feed = self.create_feed()
        
        sorted_updates = sorted(updates, key=lambda x: (not x['is_new'], x['repo']['rank']), reverse=True)
        
        for update in sorted_updates:
            repo = update['repo']
            change_info = update['change_info']
            
            description = f"{change_info}\n\n{repo['description']}"
            if repo.get('language'):
                description += f"\n\nLanguage: {repo['language']}"
            if repo.get('today_stars'):
                description += f"\n{repo['today_stars']}"
            
            entry = feed.add_entry()
            entry.title(f"{repo['repo_name']}")
            entry.link(href=repo['repo_url'])
            entry.pubDate(datetime.now(timezone.utc))
            entry.description(description)
            entry.guid(repo['repo_url'], permalink=True)
        
        rss_content = feed.rss_str(pretty=True)
        return rss_content


async def main():
    generator = GitHubTrendingRSSGenerator()
    
    print("Loading previous data...")
    previous_data = generator.load_previous_data()
    
    print("\nFetching current trending repos...")
    current_repos = await generator.fetch_trending()
    
    print(f"\nFound {len(current_repos)} trending repos")
    
    print("\nComparing with previous data...")
    updates, current_data = generator.compare_and_generate_updates(current_repos, previous_data)
    
    print(f"\nFound {len(updates)} updates")
    
    if updates:
        print("\nGenerating RSS feed...")
        rss_content = generator.generate_rss(updates)
        
        os.makedirs(generator.rss_dir, exist_ok=True)
        
        with open(generator.rss_file, 'wb') as f:
            f.write(rss_content)
        
        print(f"RSS feed saved to {generator.rss_file}")
    else:
        print("\nNo changes detected, skipping RSS generation")
    
    print("\nSaving current data...")
    generator.save_current_data(current_data)
    
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
