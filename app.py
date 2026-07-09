import streamlit as st
import pandas as pd
import numpy as np
import datetime
from scrapers.amazon import AmazonScraper
from scrapers.flipkart import FlipkartScraper
from scrapers.meesho import MeeshoScraper
from processing.cleaner import DataCleaner
from processing.analytics import CompetitorAnalyzer
from ai.listing_generator import ListingGenerator
from exports.exporter import DataExporter

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="GenAI Product Listing Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-quality professional look
st.markdown("""
<style>
    /* Styling for cards */
    .product-card {
        background-color: #fcfcfc;
        border: 1px solid #eef0f3;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .product-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .badge-amazon {
        background-color: #fef3c7;
        color: #d97706;
    }
    .badge-flipkart {
        background-color: #dbeafe;
        color: #2563eb;
    }
    .badge-meesho {
        background-color: #fce7f3;
        color: #db2777;
    }
    .badge-live {
        background-color: #d1fae5;
        color: #059669;
    }
    .badge-fallback {
        background-color: #f3f4f6;
        color: #4b5563;
    }
    .price-text {
        font-size: 1.15rem;
        font-weight: 700;
        color: #111827;
        margin-top: 4px;
    }
    .rating-text {
        font-size: 0.85rem;
        color: #4b5563;
        margin-top: 4px;
    }
    .metadata-line {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "current_stats" not in st.session_state:
    st.session_state.current_stats = None
if "current_listing" not in st.session_state:
    st.session_state.current_listing = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""

# Sidebar Branding and History
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("Listing Assistant")
    st.caption("GenAI Product Listing Generation & Competitor Scraping")
    st.markdown("---")
    
    st.subheader("Listing Preferences")
    target_audience = st.selectbox(
        "Target Audience",
        ["General Shoppers", "Tech Enthusiasts", "Professionals", "Budget Conscious", "Parents & Families", "Fitness & Active"],
        index=0,
        help="Select the core customer group you want to address."
    )
    
    tone_of_voice = st.selectbox(
        "Tone of Voice",
        ["Professional & Persuasive", "Bold & Energetic", "Friendly & Conversational", "Sophisticated & Luxury", "Witty & Fun"],
        index=0,
        help="Tone used by Gemini to draft the copy."
    )
    
    st.markdown("---")
    
    st.subheader("Search History")
    if st.session_state.search_history:
        for hist_query in reversed(st.session_state.search_history[-8:]):
            if st.button(f"🔍 {hist_query}", key=f"hist_{hist_query}", use_container_width=True):
                st.session_state.current_query = hist_query
                st.rerun()
    else:
        st.write("No queries searched yet.")

# Main Title and Overview
st.title("🛍️ GenAI Product Listing Assistant")
st.markdown(
    "Analyze competitor pricing, reviews, and catalog layouts across e-commerce "
    "marketplaces to automatically generate highly optimized, premium product listings."
)

# Search Bar Area
search_col1, search_col2 = st.columns([5, 1])
with search_col1:
    query_input = st.text_input(
        "Enter Product Name or Keywords:",
        value=st.session_state.current_query,
        placeholder="e.g. Wireless Ergonomic Mouse, Leather Laptop Sleeve, Copper Water Bottle",
        label_visibility="collapsed"
    )
with search_col2:
    search_button = st.button("Generate Listing", use_container_width=True, type="primary")

# Run Pipeline on search action
if search_button or (query_input and st.session_state.current_query != query_input and not st.session_state.current_results):
    if not query_input.strip():
        st.warning("Please enter a valid product keyword.")
    else:
        st.session_state.current_query = query_input
        if query_input not in st.session_state.search_history:
            st.session_state.search_history.append(query_input)
            
        with st.status("Analyzing Market & Crafting Listing...", expanded=True) as status:
            # 1. Scrape data
            status.update(label="Scraping competitor products (best-effort static scraping)...")
            amazon_sc = AmazonScraper()
            flipkart_sc = FlipkartScraper()
            meesho_sc = MeeshoScraper()
            
            raw_products = []
            
            # Scrape sites
            raw_products.extend(amazon_sc.scrape(query_input))
            raw_products.extend(flipkart_sc.scrape(query_input))
            raw_products.extend(meesho_sc.scrape(query_input))
            
            # 2. Clean data
            status.update(label="Cleaning and normalizing data...")
            cleaner = DataCleaner()
            df_cleaned = cleaner.clean_products(raw_products)
            st.session_state.current_results = df_cleaned
            
            # 3. Competitor Analysis
            status.update(label="Performing competitor analysis...")
            stats = CompetitorAnalyzer.analyze(df_cleaned)
            st.session_state.current_stats = stats
            
            # 4. AI Copy Generation
            status.update(label="Synthesizing copy using Google Gemini API...")
            try:
                generator = ListingGenerator()
                listing = generator.generate_listing(
                    keyword=query_input,
                    competitor_stats=stats,
                    scraped_products_df=df_cleaned,
                    target_audience=target_audience,
                    tone=tone_of_voice
                )
                st.session_state.current_listing = listing
                status.update(label="Successfully generated listing!", state="complete")
            except Exception as e:
                st.session_state.current_listing = None
                status.update(label="Competitor data compiled. AI key is missing or failed.", state="error")
                st.error(f"Failed to generate listing with Gemini: {e}")

# Render Results
if st.session_state.current_results is not None:
    df = st.session_state.current_results
    stats = st.session_state.current_stats
    listing = st.session_state.current_listing
    
    # Check if we triggered fallbacks
    any_fallback = df["is_fallback"].any()
    
    # -------------------------------------------------------------
    # SECTION 1: Competitor Market Metrics
    # -------------------------------------------------------------
    st.subheader("📊 Competitor Market Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Competitors", len(df))
    with col2:
        price_val = f"₹{stats['lowest_price']:,.2f}" if stats['lowest_price'] > 0 else "N/A"
        st.metric("Lowest Price", price_val)
    with col3:
        price_val = f"₹{stats['average_price']:,.2f}" if stats['average_price'] > 0 else "N/A"
        st.metric("Average Price", price_val)
    with col4:
        price_val = f"₹{stats['median_price']:,.2f}" if stats['median_price'] > 0 else "N/A"
        st.metric("Median Price", price_val)
    with col5:
        price_val = f"₹{stats['highest_price']:,.2f}" if stats['highest_price'] > 0 else "N/A"
        st.metric("Highest Price", price_val)
        
    # Inform the user about static scraper limits and fallbacks
    if any_fallback:
        st.info(
            "⚠️ **Anti-Bot Advisory:** One or more e-commerce sites triggered an anti-bot captcha/challenge. "
            "To keep the listing assistant fully functional, a realistic competitor backup dataset was blended "
            "into the analysis metrics."
        )
        
    # Highlight Cards
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        if stats["highest_rated_product"]:
            prod = stats["highest_rated_product"]
            st.success(
                f"🌟 **Top Rated Competitor:**\n\n"
                f"**Name:** {prod['name'][:80]}...\n\n"
                f"**Rating:** {prod['rating']} ({prod['reviews']} Reviews) | **Website:** {prod['website']}"
            )
    with h_col2:
        if stats["most_reviewed_product"]:
            prod = stats["most_reviewed_product"]
            st.info(
                f"📈 **Most Popular (Reviews):**\n\n"
                f"**Name:** {prod['name'][:80]}...\n\n"
                f"**Reviews:** {prod['reviews']} | **Price:** {prod['price']} | **Website:** {prod['website']}"
            )

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 2: AI Generated Product Listing
    # -------------------------------------------------------------
    st.subheader("✨ AI-Generated Listing Copy")
    
    if listing:
        # Layout container for AI response
        ai_box = st.container(border=True)
        with ai_box:
            tab1, tab2, tab3, tab4 = st.tabs([
                "📝 Core SEO Copy", 
                "⚡ Bullets & Features", 
                "🔧 Specifications & Tags", 
                "💸 Selling Points & CTA"
            ])
            
            with tab1:
                st.markdown(f"### 🏷️ Optimized SEO Title")
                st.code(listing["seo_title"], language="text")
                
                st.markdown("### 📱 Mobile Short Description")
                st.write(listing["short_description"])
                
                st.markdown("### 📄 Detailed Product Description")
                st.write(listing["long_description"])
                
            with tab2:
                st.markdown("### 📌 Bullet Points (Highly Converting)")
                for bullet in listing["bullets"]:
                    st.markdown(f"{bullet}")
                    
                st.markdown("---")
                st.markdown("### ✨ Core Product Features")
                for feat in listing["features"]:
                    st.markdown(f"- {feat}")
                    
            with tab3:
                st.markdown("### 🔍 Search Backend SEO Keywords")
                keywords_html = " ".join([f"<span style='background-color:#f3f4f6; padding:4px 8px; border-radius:12px; margin-right:6px; font-size:0.85rem; color:#4b5563; font-weight:500;'>#{kw}</span>" for kw in listing["keywords"]])
                st.markdown(keywords_html, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 📐 Technical Specifications")
                spec_df = pd.DataFrame(list(listing["specifications"].items()), columns=["Specification", "Value"])
                st.table(spec_df)
                
            with tab4:
                st.markdown("### 💎 Unique Selling Points (USPs)")
                for sp in listing["selling_points"]:
                    st.markdown(f"💎 **{sp}**")
                    
                st.markdown("---")
                st.markdown("### 📊 Meta Description")
                st.code(listing["meta_description"], language="text")
                
                st.markdown("### 🚀 Call To Action")
                st.success(listing["call_to_action"])

        # EXPORT BUTTONS
        st.markdown("#### 📥 Export Listing and Market Data")
        exp_col1, exp_col2, _ = st.columns([1, 1, 3])
        
        # Prepare file names
        excel_name = DataExporter.get_timestamped_filename(st.session_state.current_query, "xlsx")
        csv_name = DataExporter.get_timestamped_filename(st.session_state.current_query, "csv")
        
        # Build streams
        csv_bytes = DataExporter.export_to_csv(df)
        excel_bytes = DataExporter.export_to_excel(df, listing)
        
        with exp_col1:
            st.download_button(
                label="📥 Download CSV (Market)",
                data=csv_bytes,
                file_name=csv_name,
                mime="text/csv",
                use_container_width=True
            )
        with exp_col2:
            st.download_button(
                label="📥 Download Excel (Full)",
                data=excel_bytes,
                file_name=excel_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.warning("AI copy generation failed or was skipped. Please verify your GEMINI_API_KEY settings.")

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 3: Competitor Catalog View
    # -------------------------------------------------------------
    st.subheader("🔍 Scraped Competitor Products")
    
    # Renders cards in a grid
    grid_cols = st.columns(3)
    for i, row in df.iterrows():
        col_to_use = grid_cols[i % 3]
        with col_to_use:
            # Website specific classes
            web_lower = str(row["website"]).lower()
            badge_cls = f"badge-{web_lower}" if web_lower in ["amazon", "flipkart", "meesho"] else ""
            
            # Check is fallback
            is_fb = row.get("is_fallback", False)
            fb_badge = '<span class="badge badge-fallback">Simulated Backup</span>' if is_fb else '<span class="badge badge-live">Live Scraped</span>'
            
            # Pricing rendering
            p_val = row["raw_price"] if pd.notna(row["raw_price"]) else "N/A"
            r_val = row["raw_rating"] if pd.notna(row["raw_rating"]) else "N/A"
            rev_val = row["raw_reviews"] if pd.notna(row["raw_reviews"]) else "N/A"
            
            st.markdown(f"""
            <div class="product-card" id="card_{i}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <span class="badge {badge_cls}">{row['website']}</span>
                    {fb_badge}
                </div>
                <div class="product-title">{row['name']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                    <div class="price-text">{p_val}</div>
                    <div class="rating-text">⭐ {r_val} ({rev_val})</div>
                </div>
                <div class="metadata-line">Status: {row['availability']}</div>
                <div style="margin-top:12px; text-align:right;">
                    <a href="{row['url']}" target="_blank" style="text-decoration:none; color:#2563eb; font-size:0.85rem; font-weight:500;">View Competitor Listing →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Price Comparison Table
    with st.expander("📊 View Detailed Price Comparison Matrix Table"):
        st.dataframe(
            stats["price_comparison_table"],
            column_config={
                "name": "Product Name",
                "price": st.column_config.NumberColumn("Price (INR)", format="₹%.2f"),
                "rating": "Rating",
                "reviews": "Review Count",
                "availability": "Stock",
                "website": "Platform"
            },
            use_container_width=True,
            hide_index=True
        )
else:
    # Empty State Display
    st.info("👋 Welcome! Enter a product keyword above and click 'Generate Listing' to begin competitor research and copy drafting.")
    st.markdown("""
    ### 🚀 Key Features:
    1. **Best-Effort Market Crawling:** Crawls Amazon, Flipkart, and Meesho for real competitor listings.
    2. **Anti-Bot Failover Defense:** Automatically swaps in beautiful synthetic competitor records if marketplaces throttle requests or enforce Captcha blocks.
    3. **Google Gemini Intelligence:** Infuses competitive stats directly into `gemini-3.5-flash` for high-conversion copywriting.
    4. **Comprehensive SEO Outputs:** Generates titles, bullet points, meta briefs, search keywords, and Call-to-Actions.
    5. **Standard Exporting Suite:** Instant CSV & multi-sheet Excel spreadsheet packaging.
    """)
