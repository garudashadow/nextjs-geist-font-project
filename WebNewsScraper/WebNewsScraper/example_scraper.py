"""
Contoh implementasi scraper berita dengan ekstraksi konten yang lebih baik
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import logging
from urllib.parse import urlparse

class NewsScraperExample:
    """Contoh implementasi scraper berita"""
    
    async def parse_article_content(self, element: BeautifulSoup) -> Dict:
        """
        Ekstrak konten artikel dengan metadata lengkap
        
        Contoh hasil:
        {
            'title': 'Judul Berita',
            'content': 'Isi berita lengkap...',
            'metadata': {
                'author': 'Nama Penulis',
                'date': '2025-02-17',
                'category': 'Politik',
                'tags': ['tag1', 'tag2']
            }
        }
        """
        # 1. Ekstrak judul dengan berbagai selector
        title = None
        title_selectors = [
            'h1.article-title',
            'h1.entry-title', 
            'h1.post-title',
            '.article-header h1'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.text.strip()
                break
                
        # 2. Ekstrak konten artikel
        content = ''
        content_selectors = [
            'div.article-content',
            'div.entry-content',
            'div.post-content',
            'article .content'
        ]
        
        for selector in content_selectors:
            content_elem = element.select_one(selector)
            if content_elem:
                # Bersihkan konten dari iklan dan elemen tidak penting
                [x.extract() for x in content_elem.find_all(['script', 'style', 'iframe'])]
                paragraphs = content_elem.find_all('p')
                content = '\n'.join(p.text.strip() for p in paragraphs)
                break
                
        # 3. Ekstrak metadata dengan format yang konsisten
        metadata = {
            'author': self._extract_author(element),
            'date': self._extract_date(element),
            'category': self._extract_category(element),
            'tags': self._extract_tags(element)
        }
        
        return {
            'title': title,
            'content': content,
            'metadata': metadata,
            'extracted_at': datetime.now().isoformat()
        }
        
    def _extract_author(self, element: BeautifulSoup) -> str:
        """
        Ekstrak informasi penulis dengan berbagai format
        """
        author_selectors = [
            '.author-name',
            '.post-author',
            'span[rel="author"]',
            '.byline',
            '.entry-author'
        ]
        
        for selector in author_selectors:
            author_elem = element.select_one(selector)
            if author_elem:
                return author_elem.text.strip()
                
        return "Penulis tidak diketahui"
        
    def _extract_date(self, element: BeautifulSoup) -> str:
        """
        Ekstrak tanggal publikasi dengan berbagai format
        """
        date_selectors = [
            'time.published',
            'time.entry-date',
            'span.post-date',
            '.article-date',
            'meta[property="article:published_time"]'
        ]
        
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                # Coba ambil dari atribut datetime atau content
                date_str = date_elem.get('datetime') or date_elem.get('content') or date_elem.text
                try:
                    date = datetime.fromisoformat(date_str)
                    return date.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    return date_str.strip()
                    
        return ""
        
    def _extract_category(self, element: BeautifulSoup) -> str:
        """
        Ekstrak kategori artikel
        """
        category_selectors = [
            '.article-category',
            '.post-category',
            '.entry-category',
            '.breadcrumb .category'
        ]
        
        for selector in category_selectors:
            category_elem = element.select_one(selector)
            if category_elem:
                return category_elem.text.strip()
                
        return "Umum"
        
    def _extract_tags(self, element: BeautifulSoup) -> List[str]:
        """
        Ekstrak tag/topik artikel
        """
        tags = []
        tag_selectors = [
            '.tags a',
            '.post-tags a',
            '.article-tags a'
        ]
        
        for selector in tag_selectors:
            tag_elems = element.select(selector)
            if tag_elems:
                tags.extend([tag.text.strip() for tag in tag_elems])
                break
                
        return list(set(tags))  # Hapus duplikat

    def clean_content(self, text: str) -> str:
        """
        Bersihkan dan format teks artikel
        """
        if not text:
            return ""
            
        # Hapus karakter whitespace berlebih
        text = ' '.join(text.split())
        
        # Hapus karakter spesial tapi pertahankan tanda baca penting
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Normalisasi tanda kutip
        text = text.replace('"', '"').replace('"', '"')
        
        # Hapus spasi di awal dan akhir
        return text.strip()

"""
Contoh penggunaan:

scraper = NewsScraperExample()

# Ambil artikel
article = await scraper.parse_article_content(soup)

# Hasil akan berformat:
{
    'title': 'Judul Berita yang Sudah Bersih',
    'content': 'Isi berita yang sudah diformat...',
    'metadata': {
        'author': 'Nama Penulis',
        'date': '2025-02-17 14:30:00',
        'category': 'Politik',
        'tags': ['Pemilu', 'Pilpres', 'Indonesia']
    },
    'extracted_at': '2025-02-17T14:30:00'
}
"""
