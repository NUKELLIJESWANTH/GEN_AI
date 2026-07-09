class PromptBuilder:
    @staticmethod
    def get_system_instruction() -> str:
        """
        Defines the copywriting persona and constraints for Gemini.
        """
        return (
            "You are an Elite E-Commerce Copywriter, SEO Strategist, and Conversion Rate Optimization (CRO) Expert "
            "with 15+ years of experience crafting high-performance listings for Amazon, Shopify, and eBay.\n"
            "Your writing is compelling, authoritative, persuasive, and perfectly optimized for both algorithms "
            "and human psychology. You strictly output your analysis in standard JSON format containing only "
            "the requested keys and no extra commentary."
        )

    @staticmethod
    def build_prompt(
        keyword: str,
        competitor_stats: dict,
        scraped_products_summary: str,
        target_audience: str = "General Buyers",
        tone: str = "Professional & Persuasive"
    ) -> str:
        """
        Dynamically builds the generation prompt. Includes raw competitor list summary,
        statistical analysis (lowest/average/median prices), target audience, and tone.
        """
        avg_price = competitor_stats.get("average_price", "N/A")
        min_price = competitor_stats.get("lowest_price", "N/A")
        max_price = competitor_stats.get("highest_price", "N/A")
        
        prompt = f"""
We want to launch a new product in the following category: "{keyword}".
To stand out, we must analyze our key competitors, undercut/outvalue their offers, and present a listing that addresses customer pain points.

-------------------------------------------------------
MARKETING CONFIGURATION:
-------------------------------------------------------
- Product Category/Keyword: {keyword}
- Desired Tone: {tone} (Ensure the entire copy matches this vibe)
- Target Audience: {target_audience} (Focus on benefits, pain points, and triggers for this demographic)

-------------------------------------------------------
COMPETITOR ANALYSIS DATA (SCRAPED REAL-TIME):
-------------------------------------------------------
- Lowest Competitor Price: {min_price}
- Highest Competitor Price: {max_price}
- Average Competitor Price: {avg_price}

Summary of Top Competitor Products Found:
{scraped_products_summary}

-------------------------------------------------------
COPYWRITING INSTRUCTIONS:
-------------------------------------------------------
Generate a professional, fully-optimized e-commerce product listing. Your copy must:
1. Outperform the competitors by highlighting premium elements they missed (e.g. better materials, superior design, or high durability).
2. Justify our pricing strategy relative to the competitor average price of {avg_price}.
3. Maximize SEO keyword density naturally (no keyword stuffing).
4. Include clear features, technical specifications, and a highly urgent Call to Action.

-------------------------------------------------------
REQUIRED OUTPUT SCHEMA:
-------------------------------------------------------
You MUST return a JSON object with EXACTLY the following keys (do not add any other markdown text outside of the JSON block):

{{
  "seo_title": "A highly clickable, SEO-optimized title under 150 characters, incorporating main keywords and high-converting features.",
  "long_description": "A comprehensive, 3-paragraph product description explaining what the product is, how it works, why it is superior, and the emotional/functional transformation it offers the user.",
  "short_description": "A punchy, single-paragraph summary of the product (under 300 characters) for quick mobile reading.",
  "bullets": [
    "5 highly persuasive, benefit-first bullet points (each starting with a bolded feature, e.g. '⚙️ HEAVY-DUTY CONCRETE BUILD: ...')",
    "..."
  ],
  "features": [
    "List of 5-6 core product features explaining utility.",
    "..."
  ],
  "specifications": {{
    "Material": "...",
    "Dimensions": "...",
    "Weight": "...",
    "Color Options": "...",
    "Compatibility / Power": "..."
  }},
  "selling_points": [
    "3-4 competitive sales arguments addressing why they should buy our version over competitors.",
    "..."
  ],
  "keywords": [
    "A list of 10-15 high-volume, relevant SEO keywords, backend search terms, and tags.",
    "..."
  ],
  "meta_description": "A compelling meta description under 160 characters designed to drive high click-through rates (CTR) from Google search results.",
  "call_to_action": "An urgent, highly motivating call to action to push shoppers to purchase (e.g., 'Add to Cart now...')."
}}
"""
        return prompt.strip()
