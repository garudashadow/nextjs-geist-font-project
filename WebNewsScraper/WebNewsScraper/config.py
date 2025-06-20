import logging
from typing import Dict, List

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log', encoding='utf-8')
    ]
)

# News Sources Configuration
NEWS_SOURCES = {
    "Media Berita Umum": [
        "https://www.jpnn.com/",
        "https://www.detik.com/",
        "https://www.kompas.com/",
        "https://www.tribunnews.com/",
        "https://www.tempo.co/",
        "https://www.liputan6.com/",
        "https://www.viva.co.id/",
        "https://www.republika.co.id/",
        "https://www.merdeka.com/",
        "https://www.suara.com/",
        "https://www.thejakartapost.com/",
        "https://www.sindonews.com/",
        "https://www.indopos.co.id/",
        "https://www.kumparan.com/",
        "https://news.detik.com/",
        "https://www.bantennews.co.id/",
        "https://www.medcom.id/",
        "https://www.pikiran-rakyat.com/",
        "https://www.suaramerdeka.com/",
        "https://www.riau24.com/",
        "https://www.pontianakpost.com/"
    ],
    "Media Olahraga": [
        "https://www.bola.com/",
        "https://sport.tempo.co/",
        "https://www.indosport.com/",
        "https://olahraga.kompas.com/",
        "https://www.goal.com/id",
        "https://www.liputan6.com/bola",
        "https://www.viva.co.id/bola",
        "https://www.bolanet.com/",
        "https://www.skor.id/",
        "https://sport.detik.com/",
        "https://www.bolasport.com/",
        "https://www.ligaolahraga.com/"
    ],
    "Media Bisnis dan Keuangan": [
        "https://www.bisnis.com/",
        "https://www.kontan.co.id/",
        "https://finansial.bisnis.com/",
        "https://investor.id/",
        "https://money.id/",
        "https://ekonomi.kompas.com/",
        "https://bisnis.tempo.co/",
        "https://www.swa.co.id/",
        "https://www.marketeers.com/",
        "https://www.cermati.com/",
        "https://www.global.co.id/"
    ]
}

# Keywords for filtering news
KEYWORDS: List[str] = [
    "politik",
    "ekonomi",
    "bisnis",
    "teknologi",
    "pendidikan",
    "kesehatan",
    "olahraga",
    "kriminal",
    "korupsi",
    "pemilu",
    "bencana"
]

# Updated Request Configuration with more sophisticated headers
REQUEST_HEADERS: List[Dict[str, str]] = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    },
    {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none"
    }
]

# Site-specific headers for problematic sites
SITE_SPECIFIC_HEADERS = {
    "www.tribunnews.com": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.google.com/",
        "Origin": "https://www.google.com"
    }
}

# Scraping Configuration with increased delays and backoff
RATE_LIMIT_DELAY = 15  # increased base delay between requests
MAX_RETRIES = 3  # reduced max retries to fail faster
REQUEST_TIMEOUT = 30
MEMORY_CACHE_SIZE = 1000
BASE_RETRY_DELAY = 10  # increased base delay for exponential backoff
MAX_RETRY_DELAY = 60  # reduced maximum delay between retries

# List of temporarily problematic sites
SKIP_SITES = [
    "www.indopos.co.id",
    "www.pontianakpost.com"
]

# Cookie settings
ENABLE_COOKIES = True
COOKIE_EXPIRY = 3600  # 1 hour

# Notification Configuration
NOTIFICATION_INTERVAL = 300  # 5 minutes in seconds