import time
import random
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from config import DEFAULT_HEADERS, DEFAULT_TIMEOUT, MAX_RETRIES, BACKOFF_FACTOR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ScraperUtils")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def get_random_headers() -> dict:
    """Returns a copy of DEFAULT_HEADERS with a randomized User-Agent."""
    headers = DEFAULT_HEADERS.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    return headers

class ScraperSession:
    """
    Wrapper around requests.Session to standardise connection pooling,
    retries, headers, timeouts, and error handling.
    """
    def __init__(self):
        self.session = requests.Session()
        
        # Configure retry mechanism
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def fetch_page(self, url: str, headers: dict = None, timeout: int = DEFAULT_TIMEOUT) -> str:
        """
        Fetches an HTML page and returns its text content.
        Returns an empty string if there's any failure.
        """
        if not headers:
            headers = get_random_headers()
            
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, headers=headers, timeout=timeout)
            
            # If rate limited or blocked, we log it
            if response.status_code == 403:
                logger.warning(f"Access forbidden (403) for URL: {url}. Might be anti-bot block.")
                return ""
            elif response.status_code == 429:
                logger.warning(f"Rate limited (429) for URL: {url}. Backing off.")
                return ""
                
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return ""

def clean_extracted_text(text: str) -> str:
    """Helper to remove excess whitespace and clean parsed HTML text."""
    if not text:
        return ""
    return " ".join(text.strip().split())
