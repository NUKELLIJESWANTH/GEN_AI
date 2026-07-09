import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Scraper Configuration
DEFAULT_TIMEOUT = 15  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5

# Standard Headers to mimic a browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Supported Sites
SITES_CONFIG = {
    "amazon": {
        "name": "Amazon",
        "url_template": "https://www.amazon.in/s?k={query}",  # Targeting India version for demonstration
        "enabled": True,
    },
    "flipkart": {
        "name": "Flipkart",
        "url_template": "https://www.flipkart.com/search?q={query}",
        "enabled": True,
    },
    "meesho": {
        "name": "Meesho",
        "url_template": "https://www.meesho.com/search?q={query}",
        "enabled": True,
    }
}
