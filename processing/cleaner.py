import re
import pandas as pd
import numpy as np
from scrapers.scraper_utils import logger

class DataCleaner:
    @staticmethod
    def normalize_price(price_str: str) -> float:
        """
        Extracts a clean numeric float representation from a price string.
        Examples: '₹1,249' -> 1249.0, '$45.99' -> 45.99, 'N/A' -> None
        """
        if not price_str or pd.isna(price_str):
            return None
        
        # Remove commas, currency symbols, and spaces
        cleaned = re.sub(r'[^\d\.]', '', str(price_str))
        
        # If price string contains multiple decimals (e.g. error), take the first match
        try:
            if cleaned:
                return float(cleaned)
        except ValueError:
            pass
        return None

    @staticmethod
    def extract_rating(rating_str: str) -> float:
        """
        Extracts numerical float rating from standard strings.
        Examples: '4.3 out of 5 stars' -> 4.3, '4.2 ★' -> 4.2, 'N/A' -> None
        """
        if not rating_str or pd.isna(rating_str):
            return None
            
        cleaned = str(rating_str).strip()
        # Find any decimal or integer number at the start or mid of string
        match = re.search(r'(\d\.\d|\d)', cleaned)
        if match:
            try:
                val = float(match.group(1))
                if 0.0 <= val <= 5.0:
                    return val
            except ValueError:
                pass
        return None

    @staticmethod
    def extract_reviews(reviews_str: str) -> int:
        """
        Extracts integer count of reviews from strings.
        Examples: '(1,240 Reviews)' -> 1240, '350' -> 350, 'N/A' -> 0
        """
        if not reviews_str or pd.isna(reviews_str):
            return 0
            
        cleaned = str(reviews_str).strip()
        # Remove everything except digits
        digits_only = re.sub(r'[^\d]', '', cleaned)
        if digits_only:
            try:
                return int(digits_only)
            except ValueError:
                pass
        return 0

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Checks if a URL is validly formatted."""
        if not url or pd.isna(url):
            return False
        return str(url).startswith(("http://", "https://"))

    def clean_products(self, raw_products: list) -> pd.DataFrame:
        """
        Ingests a list of raw product dicts, cleans, deduplicates,
        normalizes each field, and returns a clean Pandas DataFrame.
        """
        if not raw_products:
            logger.warning("Empty product list passed to DataCleaner.")
            return pd.DataFrame(columns=[
                "name", "price", "rating", "reviews", "availability", 
                "image", "url", "website", "is_fallback"
            ])

        cleaned_list = []
        for p in raw_products:
            try:
                name = str(p.get("name", "")).strip()
                if not name or name == "None":
                    continue
                
                raw_price = p.get("price", "")
                price = self.normalize_price(raw_price)
                
                raw_rating = p.get("rating", "")
                rating = self.extract_rating(raw_rating)
                
                raw_reviews = p.get("reviews", "")
                reviews = self.extract_reviews(raw_reviews)
                
                url = p.get("url", "").strip()
                if not self.is_valid_url(url):
                    url = "https://www.google.com"  # Safe default fallback url

                # Standardize website names
                website = str(p.get("website", "")).strip().capitalize()
                if website not in ["Amazon", "Flipkart", "Meesho"]:
                    website = "Competitor"

                cleaned_list.append({
                    "name": name,
                    "raw_price": raw_price,
                    "price": price if price is not None else np.nan,
                    "raw_rating": raw_rating,
                    "rating": rating if rating is not None else np.nan,
                    "raw_reviews": raw_reviews,
                    "reviews": reviews,
                    "availability": str(p.get("availability", "In Stock")).strip(),
                    "image": p.get("image", "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=500&auto=format&fit=crop&q=60"),
                    "url": url,
                    "website": website,
                    "is_fallback": p.get("is_fallback", False)
                })
            except Exception as e:
                logger.error(f"Error cleaning product record: {e}")
                continue

        df = pd.DataFrame(cleaned_list)
        
        # Deduplicate based on product name (case-insensitive) or URL
        if not df.empty:
            df["name_lower"] = df["name"].str.lower()
            df = df.drop_duplicates(subset=["name_lower"])
            df = df.drop_duplicates(subset=["url"])
            df = df.drop(columns=["name_lower"])
            
            # Fill missing reviews with 0 and sort
            df["reviews"] = df["reviews"].fillna(0).astype(int)
            
            # Drop entries where name is missing
            df = df.dropna(subset=["name"])

        return df.reset_index(drop=True)
