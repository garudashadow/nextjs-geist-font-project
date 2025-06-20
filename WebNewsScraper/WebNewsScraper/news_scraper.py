import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
from datetime import datetime
import json
import random
from urllib.parse import urlparse

from config import (
    NEWS_SOURCES, KEYWORDS, REQUEST_HEADERS, RATE_LIMIT_DELAY,
    MAX_RETRIES, REQUEST_TIMEOUT, MEMORY_CACHE_SIZE, SKIP_SITES, BASE_RETRY_DELAY, MAX_RETRY_DELAY, SITE_SPECIFIC_HEADERS
)
from utils import MemoryCache, clean_text, normalize_url, contains_keywords, log_error
from id_helpers import parse_indo_date, clean_indo_text, extract_location

class NewsScraperAsync:
    def __init__(self):
        self.cache = MemoryCache(max_size=MEMORY_CACHE_SIZE)
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize aiohttp session with default headers and cookie support"""
        if not self.session:
            initial_headers = self._get_random_headers()
            cookie_jar = aiohttp.CookieJar(unsafe=True)
            self.session = aiohttp.ClientSession(
                headers=initial_headers,
                cookie_jar=cookie_jar,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            )

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    def _get_random_headers(self) -> Dict[str, str]:
        """Get random headers to rotate between requests"""
        return random.choice(REQUEST_HEADERS)

    async def _get_headers_for_site(self, url: str) -> Dict[str, str]:
        """Get headers with site-specific additions if needed"""
        base_headers = self._get_random_headers()
        domain = urlparse(url).netloc
        if domain in SITE_SPECIFIC_HEADERS:
            base_headers.update(SITE_SPECIFIC_HEADERS[domain])
        return base_headers

    async def fetch_page(self, url: str, retries: int = 0) -> Optional[str]:
        """Fetch page content with enhanced retry logic and error handling"""
        if not self.session:
            await self.initialize()

        domain = urlparse(url).netloc
        if domain in SKIP_SITES:
            logging.warning(f"Skipping known problematic site: {url}")
            return None

        if retries >= MAX_RETRIES:
            logging.error(f"Max retries reached for {url}")
            return None

        try:
            delay = min(BASE_RETRY_DELAY * (2 ** retries), MAX_RETRY_DELAY)
            jitter = random.uniform(0.5, 1.5)
            delay = delay * jitter

            headers = await self._get_headers_for_site(url)
            if self.session:
                self.session.headers.update(headers)

                # Log request details for debugging
                if domain == "www.tribunnews.com":
                    logging.info(f"Attempting request to {url}")
                    logging.info(f"Headers being used: {json.dumps(headers, indent=2)}")

                async with self.session.get(
                    url,
                    ssl=False,
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:
                    if response.status == 200:
                        try:
                            content = await response.text()
                            logging.info(f"Successfully fetched content from {url}")
                            return content
                        except Exception as e:
                            logging.error(f"Error decoding content from {url}: {e}")
                            return None
                    elif response.status == 403:
                        logging.warning(f"Access forbidden for {url}, response headers: {dict(response.headers)}")
                        if self.session and self.session.cookie_jar:
                            self.session.cookie_jar.clear_domain(domain)
                        await asyncio.sleep(delay)
                        return await self.fetch_page(url, retries + 1)
                    elif response.status == 429:
                        wait_time = int(response.headers.get('Retry-After', delay))
                        logging.warning(f"Rate limited on {url}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                        return await self.fetch_page(url, retries + 1)
                    elif response.status >= 500:
                        logging.warning(f"Server error {response.status} for {url}, retrying...")
                        await asyncio.sleep(delay)
                        return await self.fetch_page(url, retries + 1)
                    else:
                        logging.warning(f"Failed to fetch {url}, status: {response.status}")
                        return None

        except aiohttp.ClientError as e:
            logging.error(f"Connection error for {url}: {e}")
            await asyncio.sleep(delay)
            return await self.fetch_page(url, retries + 1)
        except asyncio.TimeoutError:
            logging.error(f"Timeout error for {url}")
            await asyncio.sleep(delay)
            return await self.fetch_page(url, retries + 1)
        except Exception as e:
            logging.error(f"Unexpected error fetching {url}: {e}")
            return None

    async def parse_article(self, html: str, base_url: str) -> List[Dict]:
        """Parse HTML content and extract articles with enhanced metadata"""
        articles = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Find article elements with improved selectors
            article_elements = soup.find_all(
                ['article', 'div', 'h3'],
                class_=lambda x: isinstance(x, str) and any(
                    c in x.lower() for c in ['article', 'news', 'post', 'berita', 'content']
                )
            )

            for element in article_elements:
                # Extract title with multiple selectors
                title_element = element.find(['h1', 'h2', 'h3', 'a'])
                if not title_element:
                    continue

                title = clean_indo_text(title_element.get_text())
                url = normalize_url(base_url, title_element.get('href', ''))

                if not title or not url:
                    continue

                # Extract metadata with improved parsing
                metadata = {
                    'author': self._extract_author(element),
                    'published_date': parse_indo_date(self._extract_date(element)),
                    'category': self._extract_category(element),
                    'description': self._extract_description(element),
                    'location': extract_location(self._extract_description(element))
                }

                # Extract full content if available
                content = self._extract_full_content(element)
                if content:
                    metadata['full_content'] = content

                if not contains_keywords(title + ' ' + metadata['description'], KEYWORDS):
                    continue

                article = {
                    'title': title,
                    'url': url,
                    'source': base_url,
                    'metadata': metadata,
                    'timestamp': datetime.now().isoformat()
                }

                if not self.cache.is_duplicate(article):
                    articles.append(article)
                    self.cache.add_article(article)
                    logging.info(f"📰 Artikel baru ditemukan: {title}")

        except Exception as e:
            log_error(e, f"parse_article: {base_url}")

        return articles

    def _extract_author(self, element) -> str:
        """Extract author information with multiple selectors"""
        author_selectors = [
            '.author-name', '.post-author', 'span[rel="author"]',
            '.byline', '.entry-author', '.penulis', '.journalist'
        ]

        for selector in author_selectors:
            author_elem = element.select_one(selector)
            if author_elem:
                return clean_indo_text(author_elem.get_text())

        # Fallback to searching by class content
        author_element = element.find(
            ['span', 'div', 'p', 'a'],
            class_=lambda x: isinstance(x, str) and any(
                c in x.lower() for c in ['author', 'writer', 'penulis', 'journalist']
            )
        )
        return clean_indo_text(author_element.get_text()) if author_element else "Tidak disebutkan"

    def _extract_date(self, element) -> str:
        """Extract publication date with multiple selectors"""
        date_selectors = [
            'time.published', 'time.entry-date', 'span.post-date',
            '.article-date', 'meta[property="article:published_time"]'
        ]

        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get('content') or date_elem.text
                return clean_indo_text(date_str)

        # Fallback to searching by class content
        date_element = element.find(
            ['time', 'span', 'div', 'p'],
            class_=lambda x: isinstance(x, str) and any(
                c in x.lower() for c in ['date', 'time', 'tanggal', 'waktu', 'published']
            )
        )
        return clean_indo_text(date_element.get_text()) if date_element else ""

    def _extract_category(self, element) -> str:
        """Extract article category with multiple selectors"""
        category_selectors = [
            '.article-category', '.post-category', '.entry-category',
            '.breadcrumb .category', '.kategori', '.rubrik'
        ]

        for selector in category_selectors:
            category_elem = element.select_one(selector)
            if category_elem:
                return clean_indo_text(category_elem.get_text())

        category_element = element.find(
            ['a', 'span', 'div'],
            class_=lambda x: isinstance(x, str) and any(
                c in x.lower() for c in ['category', 'kategori', 'rubrik', 'kanal']
            )
        )
        return clean_indo_text(category_element.get_text()) if category_element else "Umum"

    def _extract_description(self, element) -> str:
        """Extract article description with multiple selectors"""
        desc_selectors = [
            '.article-excerpt', '.post-excerpt', '.entry-summary',
            'meta[name="description"]', '.ringkasan'
        ]

        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                content = desc_elem.get('content') or desc_elem.text
                return clean_indo_text(content)

        desc_element = element.find(
            ['p', 'div'],
            class_=lambda x: isinstance(x, str) and any(
                c in x.lower() for c in ['desc', 'summary', 'excerpt', 'ringkasan']
            )
        )
        return clean_indo_text(desc_element.get_text()) if desc_element else ""

    def _extract_full_content(self, element) -> Optional[str]:
        """Extract full article content if available"""
        content_selectors = [
            'div.article-content', 'div.entry-content', 'div.post-content',
            'article .content', '.body-text'
        ]

        for selector in content_selectors:
            content_elem = element.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for unwanted in content_elem.find_all(['script', 'style', 'iframe', 'form']):
                    unwanted.decompose()

                # Extract paragraphs
                paragraphs = content_elem.find_all('p')
                if paragraphs:
                    content = '\n'.join(clean_indo_text(p.get_text()) for p in paragraphs)
                    return content if content.strip() else None

        return None

    async def scrape_source(self, source_url: str) -> List[Dict]:
        """Scrape a single news source"""
        html = await self.fetch_page(source_url)
        if not html:
            return []

        await asyncio.sleep(RATE_LIMIT_DELAY)
        return await self.parse_article(html, source_url)

    async def scrape_all_sources(self) -> List[Dict]:
        """Scrape all configured news sources with concurrent execution"""
        all_articles = []

        for category, sources in NEWS_SOURCES.items():
            tasks = []
            for source_url in sources:
                task = asyncio.create_task(self.scrape_source(source_url))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    log_error(result, "scrape_all_sources")
                elif isinstance(result, list):
                    all_articles.extend(result)

        return all_articles

    def save_articles(self, articles: List[Dict]):
        """Save articles to JSON file with enhanced structure and error handling"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"articles_{timestamp}.json"

            # Deduplicate articles based on title and URL
            unique_articles = {}
            for article in articles:
                key = f"{article['title']}::{article['url']}"
                if key not in unique_articles:
                    unique_articles[key] = article

            # Convert back to list and group by category
            deduplicated_articles = list(unique_articles.values())
            categorized_articles = {}
            for article in deduplicated_articles:
                source_domain = urlparse(article['source']).netloc
                category = next(
                    (cat for cat, urls in NEWS_SOURCES.items()
                     if any(url in article['source'] for url in urls)),
                    "Lainnya"
                )

                if category not in categorized_articles:
                    categorized_articles[category] = []
                categorized_articles[category].append(article)

            output_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_articles": len(deduplicated_articles),
                    "categories": {
                        cat: {
                            "count": len(arts),
                            "sources": list(set(art['source'] for art in arts))
                        } for cat, arts in categorized_articles.items()
                    }
                },
                "articles": categorized_articles
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logging.info(f"✅ Berhasil menyimpan {len(deduplicated_articles)} artikel ke {filename}")
            for category, info in output_data["metadata"]["categories"].items():
                logging.info(f"📊 {category}: {info['count']} artikel dari {len(info['sources'])} sumber")

        except Exception as e:
            log_error(e, "save_articles")
            logging.error(f"❌ Gagal menyimpan artikel: {str(e)}")

async def main():
    scraper = NewsScraperAsync()
    try:
        await scraper.initialize()
        while True:
            logging.info("Starting news scraping cycle...")

            articles = await scraper.scrape_all_sources()
            if articles:
                scraper.save_articles(articles)
                logging.info(f"Successfully scraped {len(articles)} new articles")
            else:
                logging.info("No new articles found")

            logging.info("Waiting for next cycle...")
            await asyncio.sleep(300)  # 5 minutes between cycles

    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as e:
        log_error(e, "main")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())