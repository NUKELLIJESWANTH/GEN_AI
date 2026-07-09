import pandas as pd
import numpy as np
from scrapers.scraper_utils import logger

class CompetitorAnalyzer:
    @staticmethod
    def analyze(df: pd.DataFrame) -> dict:
        """
        Performs competitive analysis on the clean product DataFrame.
        Returns a rich dictionary of stats, figures, and targeted highlights.
        """
        if df.empty:
            logger.warning("Empty DataFrame passed to CompetitorAnalyzer.")
            return {
                "lowest_price": 0.0,
                "highest_price": 0.0,
                "average_price": 0.0,
                "median_price": 0.0,
                "lowest_price_product": None,
                "highest_price_product": None,
                "highest_rated_product": None,
                "most_reviewed_product": None,
                "products_by_website": {},
                "price_comparison_table": pd.DataFrame()
            }

        # Filter rows with non-null prices for price calculations
        price_df = df.dropna(subset=["price"])
        
        # Core Price Calculations
        if not price_df.empty:
            lowest_price = float(price_df["price"].min())
            highest_price = float(price_df["price"].max())
            average_price = float(price_df["price"].mean())
            median_price = float(price_df["price"].median())
            
            # Find specific products
            lowest_row = price_df.loc[price_df["price"].idxmin()]
            highest_row = price_df.loc[price_df["price"].idxmax()]
            
            lowest_price_product = {
                "name": lowest_row["name"],
                "price": lowest_row["price"],
                "website": lowest_row["website"],
                "url": lowest_row["url"]
            }
            
            highest_price_product = {
                "name": highest_row["name"],
                "price": highest_row["price"],
                "website": highest_row["website"],
                "url": highest_row["url"]
            }
        else:
            lowest_price = highest_price = average_price = median_price = 0.0
            lowest_price_product = highest_price_product = None

        # Filter rows with non-null ratings
        rating_df = df.dropna(subset=["rating"])
        if not rating_df.empty:
            # Sort by rating (desc) and reviews (desc) to find the best rated product
            highest_rated_row = rating_df.sort_values(by=["rating", "reviews"], ascending=False).iloc[0]
            highest_rated_product = {
                "name": highest_rated_row["name"],
                "rating": highest_rated_row["rating"],
                "reviews": highest_rated_row["reviews"],
                "website": highest_rated_row["website"],
                "url": highest_rated_row["url"]
            }
        else:
            highest_rated_product = None

        # Filter rows with reviews
        review_df = df[df["reviews"] > 0]
        if not review_df.empty:
            most_reviewed_row = review_df.sort_values(by="reviews", ascending=False).iloc[0]
            most_reviewed_product = {
                "name": most_reviewed_row["name"],
                "reviews": most_reviewed_row["reviews"],
                "price": most_reviewed_row["price"] if not pd.isna(most_reviewed_row["price"]) else "N/A",
                "website": most_reviewed_row["website"],
                "url": most_reviewed_row["url"]
            }
        else:
            most_reviewed_product = None

        # Count of products by website
        products_by_website = df["website"].value_counts().to_dict()

        # Build comparison table
        price_comparison_table = df[[
            "name", "price", "rating", "reviews", "availability", "website"
        ]].copy()
        
        price_comparison_table = price_comparison_table.sort_values(by="price", ascending=True)

        return {
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "average_price": round(average_price, 2),
            "median_price": median_price,
            "lowest_price_product": lowest_price_product,
            "highest_price_product": highest_price_product,
            "highest_rated_product": highest_rated_product,
            "most_reviewed_product": most_reviewed_product,
            "products_by_website": products_by_website,
            "price_comparison_table": price_comparison_table
        }
