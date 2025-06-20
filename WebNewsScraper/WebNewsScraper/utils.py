import hashlib
from typing import Dict, List
import re
from urllib.parse import urljoin
import logging
from collections import OrderedDict

class MemoryCache:
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size

    def add_article(self, article: Dict) -> None:
        """Add article to cache with LRU eviction"""
        article_hash = self._generate_hash(article)
        if article_hash not in self.cache:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[article_hash] = article

    def is_duplicate(self, article: Dict) -> bool:
        """Check if article is already in cache"""
        return self._generate_hash(article) in self.cache

    @staticmethod
    def _generate_hash(article: Dict) -> str:
        """Generate unique hash for article based on title and URL"""
        content = f"{article['title']}{article['url']}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters but keep Indonesian diacritics
    text = re.sub(r'[^\w\s\-\']|_', ' ', text)
    # Normalize whitespace
    text = text.strip()
    return text

def normalize_url(base_url: str, url: str) -> str:
    """Normalize relative URLs to absolute URLs"""
    if not url:
        return ""
    if url.startswith(('http://', 'https://')):
        return url
    return urljoin(base_url, url)

def contains_keywords(text: str, keywords: List[str]) -> bool:
    """Check if text contains any of the keywords"""
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

def log_error(error: Exception, source: str) -> None:
    """Log error with context"""
    logging.error(f"Error in {source}: {str(error)}", exc_info=True)
