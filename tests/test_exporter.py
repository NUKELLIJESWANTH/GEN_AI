import unittest
import pandas as pd
from exports.exporter import DataExporter

class TestDataExporter(unittest.TestCase):
    def test_get_timestamped_filename(self):
        filename_csv = DataExporter.get_timestamped_filename("Smart Watch", "csv")
        self.assertTrue(filename_csv.startswith("Smart_Watch_"))
        self.assertTrue(filename_csv.endswith(".csv"))

        filename_special = DataExporter.get_timestamped_filename("Super-Cool! Item @2026", "xlsx")
        self.assertTrue("!" not in filename_special)
        self.assertTrue("@" not in filename_special)
        self.assertTrue(filename_special.endswith(".xlsx"))

    def test_export_to_csv(self):
        df = pd.DataFrame([{"name": "P1", "price": 100}])
        csv_bytes = DataExporter.export_to_csv(df)
        self.assertIsInstance(csv_bytes, bytes)
        self.assertTrue(len(csv_bytes) > 0)

    def test_export_to_excel(self):
        df = pd.DataFrame([{"name": "P1", "price": 100, "website": "Amazon"}])
        ai_listing = {
            "seo_title": "Best Product",
            "bullets": ["Bullet 1", "Bullet 2"],
            "features": ["Feat 1"],
            "specifications": {"Material": "Concrete"}
        }
        excel_bytes = DataExporter.export_to_excel(df, ai_listing)
        self.assertIsInstance(excel_bytes, bytes)
        self.assertTrue(len(excel_bytes) > 0)

if __name__ == "__main__":
    unittest.main()
