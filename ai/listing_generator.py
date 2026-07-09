import logging
import pandas as pd
from ai.gemini_client import GeminiClient
from ai.prompt_builder import PromptBuilder

logger = logging.getLogger("ListingGenerator")

class ListingGenerator:
    def __init__(self):
        self.client = GeminiClient()

    def _summarize_competitor_products(self, df: pd.DataFrame) -> str:
        """
        Formats a clean, bulleted summary of competitor products 
        from the Pandas DataFrame to embed in the prompt.
        """
        if df.empty:
            return "No real competitor listings found. General market average pricing is assumed."

        summary_lines = []
        # Take up to top 5 products for summarizing
        summary_df = df.head(5)
        
        for idx, row in summary_df.iterrows():
            name = row.get("name", "Unknown Product")
            price = row.get("raw_price", "N/A") if pd.notna(row.get("raw_price")) else "N/A"
            rating = row.get("raw_rating", "N/A") if pd.notna(row.get("raw_rating")) else "N/A"
            reviews = row.get("reviews", 0)
            website = row.get("website", "Unknown")
            is_fallback_tag = "[Simulated Backup]" if row.get("is_fallback", False) else "[Live Scraped]"
            
            line = (
                f"- {is_fallback_tag} {name} | Website: {website} | Price: {price} | "
                f"Rating: {rating} | Reviews: {reviews}"
            )
            summary_lines.append(line)
            
        return "\n".join(summary_lines)

    def generate_listing(
        self,
        keyword: str,
        competitor_stats: dict,
        scraped_products_df: pd.DataFrame,
        target_audience: str = "General Buyers",
        tone: str = "Professional & Persuasive"
    ) -> dict:
        """
        Orchestrates the entire generation pipeline: summarizing competitor products,
        building prompts, querying Gemini, and validating the output.
        """
        logger.info(f"Generating listing for keyword: '{keyword}'")
        
        # 1. Summarize scraped products
        products_summary = self._summarize_competitor_products(scraped_products_df)
        
        # 2. Build detailed prompt
        prompt = PromptBuilder.build_prompt(
            keyword=keyword,
            competitor_stats=competitor_stats,
            scraped_products_summary=products_summary,
            target_audience=target_audience,
            tone=tone
        )
        
        # 3. Get system instruction
        system_instruction = PromptBuilder.get_system_instruction()
        
        # 4. Invoke Gemini client
        raw_listing_json = self.client.generate_structured_listing(
            prompt=prompt,
            system_instruction=system_instruction
        )
        
        # 5. Post-process & validate structure (filling in default values if keys are missing)
        validated_listing = self._validate_and_fill_defaults(raw_listing_json, keyword)
        
        return validated_listing

    def _validate_and_fill_defaults(self, data: dict, keyword: str) -> dict:
        """
        Ensures all expected keys are present in the response dictionary.
        Prevents downstream KeyError crashes in the Streamlit UI.
        """
        required_keys = {
            "seo_title": f"Premium {keyword.title()} - Ultimate Quality Edition",
            "long_description": f"Introducing the brand new premium {keyword}. Designed with the highest quality materials, this product offers unmatched comfort, durability, and daily utility. Perfect for modern users looking to upgrade their setup.",
            "short_description": f"The finest {keyword} crafted for modern needs, blending top-tier performance with elegant design.",
            "bullets": [
                "✨ PREMIUM CRAFTSMANSHIP: Made with elite-grade materials for ultimate resilience.",
                "⚙️ ADVANCED ENGINEERING: Specially designed to outperform competitor models.",
                "🛡️ SAFE & COMFORTABLE: Created with user comfort as the absolute highest priority.",
                "💼 SLEEK DESIGN: Fits in beautifully with any modern environment or aesthetic.",
                "📦 SATISFACTION GUARANTEED: Enjoy complete peace of mind with our 100% money-back guarantee."
            ],
            "features": [
                "Ergonomic, user-safe construction",
                "Built using durable, premium-grade components",
                "Includes enhanced functionality over standard models",
                "Lightweight and highly portable",
                "Available in multiple colors and style options"
            ],
            "specifications": {
                "Material": "Premium Composite",
                "Dimensions": "Standard Retail Fit",
                "Weight": "Optimized lightweight design",
                "Color Options": "Charcoal Black / Slate Gray",
                "Warranty": "1-Year Manufacturer Warranty"
            },
            "selling_points": [
                "Better pricing structure than the leading competitor average.",
                "High-durability reinforced design guarantees a longer product lifespan.",
                "Top-tier features normally reserved for double the price."
            ],
            "keywords": [keyword, f"buy {keyword}", f"best {keyword}", f"premium {keyword}", "e-commerce best seller"],
            "meta_description": f"Buy the ultimate {keyword} online. High quality, excellent pricing, and premium features. Order now for fast delivery!",
            "call_to_action": "Click 'Add to Cart' now to secure yours while stocks last!"
        }
        
        # Backfill any missing fields
        for key, default_val in required_keys.items():
            if key not in data or not data[key]:
                data[key] = default_val
                logger.warning(f"Gemini output missed key '{key}'. Backfilled with high-fidelity template.")
                
        # Handle nested dictionary validation for specifications
        if isinstance(data.get("specifications"), dict):
            if not data["specifications"]:
                data["specifications"] = required_keys["specifications"]
        else:
            data["specifications"] = required_keys["specifications"]
            
        return data
