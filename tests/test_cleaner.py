import unittest
import pandas as pd
import numpy as np
from processing.cleaner import DataCleaner

class TestDataCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = DataCleaner()

    def test_normalize_price(self):
        self.assertEqual(self.cleaner.normalize_price("₹1,249"), 1249.0)
        self.assertEqual(self.cleaner.normalize_price("$45.99"), 45.99)
        self.assertEqual(self.cleaner.normalize_price("299"), 299.0)
        self.assertIsNone(self.cleaner.normalize_price("N/A"))
        self.assertIsNone(self.cleaner.normalize_price(""))

    def test_extract_rating(self):
        self.assertEqual(self.cleaner.extract_rating("4.3 out of 5 stars"), 4.3)
        self.assertEqual(self.cleaner.extract_rating("4.2 ★"), 4.2)
        self.assertEqual(self.cleaner.extract_rating("4 ★"), 4.0)
        self.assertEqual(self.cleaner.extract_rating("5"), 5.0)
        self.assertIsNone(self.cleaner.extract_rating("N/A"))

    def test_extract_reviews(self):
        self.assertEqual(self.cleaner.extract_reviews("(1,240 Reviews)"), 1240)
        self.assertEqual(self.cleaner.extract_reviews("350 ratings"), 350)
        self.assertEqual(self.cleaner.extract_reviews(""), 0)

    def test_clean_products(self):
        raw_data = [
            {
                "name": "Test Product 1",
                "price": "₹1,000",
                "rating": "4.5",
                "reviews": "100",
                "website": "amazon",
                "url": "https://www.amazon.in/dp/B0001"
            },
            {
                "name": "Test Product 1",  # Duplicate name
                "price": "₹1,200",
                "rating": "4.6",
                "reviews": "120",
                "website": "amazon",
                "url": "https://www.amazon.in/dp/B0001-dup"
            },
            {
                "name": "Test Product 2",
                "price": "N/A",
                "rating": "N/A",
                "reviews": "N/A",
                "website": "flipkart",
                "url": "https://www.flipkart.com/dp/B0002"
            }
        ]
        
        df_clean = self.cleaner.clean_products(raw_data)
        # Check deduplication
        self.assertEqual(len(df_clean), 2)
        
        # Check normalization
        row1 = df_clean.iloc[0]
        self.assertEqual(row1["name"], "Test Product 1")
        self.assertEqual(row1["price"], 1000.0)
        self.assertEqual(row1["rating"], 4.5)
        self.assertEqual(row1["reviews"], 100)
        self.assertEqual(row1["website"], "Amazon")

if __name__ == "__main__":
    unittest.main()
