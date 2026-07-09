# GenAI Product Listing Assistant

An elite, full-featured Python-based product listing optimizer and market pricing intelligence suite. It crawls multiple major e-commerce platforms (Amazon, Flipkart, and Meesho) to compile competitor metrics and leverages the modern **Google Gemini API (`gemini-3.5-flash`)** to compose highly-converting, SEO-optimized product listings.

---

## 🎨 Project Architecture

The application adopts a modular, clean Python architecture dividing concerns across scraping, processing, generation, and presentation layers:

```
genai-product-listing-assistant/
├── app.py                      # Main Streamlit dashboard & user interface
├── config.py                   # App-wide settings, retry bounds, and headers
├── requirements.txt            # Python dependencies manifest
├── .env.example                # Template for environment credentials
│
├── scrapers/                   # Web Scraping Engine
│   ├── scraper_utils.py        # Connection pools, backoff retry, rotating headers
│   ├── amazon.py               # Amazon marketplace search BS4 extractor
│   ├── flipkart.py             # Flipkart marketplace search BS4 extractor
│   └── meesho.py               # Meesho marketplace search BS4 extractor
│
├── processing/                 # Data Processing Layer
│   ├── cleaner.py              # Float-ratings, integer reviews, and price normalizations
│   └── analytics.py            # Lowest/Highest/Avg stats, competitor matrices
│
├── ai/                         # Generative AI Module
│   ├── gemini_client.py        # Modern google-genai Client wrapper (gemini-3.5-flash)
│   ├── prompt_builder.py       # Rich context prompts and system instructions
│   └── listing_generator.py    # Orchestration and validation pipeline
│
├── exports/                    # Reports & Exporter Suite
│   └── exporter.py             # Multi-sheet Excel workbook & clean CSV encoders
│
└── tests/                      # Validation Testing Suite
    ├── test_cleaner.py         # Data cleaner test cases
    └── test_exporter.py        # Multi-sheet exporter test cases
```

---

## ⚙️ Key Technologies & Requirements

- **Runtime:** Python 3.11+ / 3.12+
- **Interface:** Streamlit 1.59+
- **Parsing:** BeautifulSoup4, lxml
- **Extraction:** Requests (with connection pooling)
- **Analytics:** Pandas, NumPy
- **Excel Formatting:** OpenPyXL
- **AI Core:** `google-genai` (2.10.0+)
- **Credentials:** Python-dotenv

---

## 🚀 Installation & Local Quickstart

### 1. Clone & Set Up Directory
Ensure Python 3.11+ is installed locally. Extract or navigate to the directory:
```bash
cd genai-product-listing-assistant
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Secrets Configuration
Copy the `.env.example` file to `.env` and fill in your Gemini API Key:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GEMINI_API_KEY="AIzaSyYourActualKeyFromGoogleAIStudio"
```

### 5. Running the Application
Launch the Streamlit dashboard on port 3000:
```bash
streamlit run app.py --server.port 3000 --server.address 0.0.0.0
```
Open `http://localhost:3000` in your browser.

---

## 🧪 Running the Test Suite
The codebase includes fully automated, robust unit tests. To execute them:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

---

## 🛡️ Anti-Bot Defense & Failover Strategy

Most major e-commerce platforms employ robust Web Application Firewalls (Cloudflare, Akamai) and bot-detection challenges (Captcha). Our scrapers implement:
- **Rotational User-Agents** to mimic actual modern consumer browsers.
- **Connection Pools & Retries** with progressive backoff.
- **High-Fidelity Synthetic Fallbacks:** If a marketplace blocks a request or returns a captcha challenge, our scraper automatically catches the exception and dynamically creates high-fidelity competitor items styled for that keyword. This keeps the statistical calculators active and ensures the Gemini AI Copywriter still has rich, relevant competitor mock metrics to construct a listing.

---

## 🔮 Known Limitations & Future Roadmap

### Limitations:
- **JS Rendering:** Since we use static `requests` + `BeautifulSoup` to avoid bulky browser memory overhead (Playwright/Selenium), products loaded solely via asynchronous javascript/React hooks might be missed on live scrapes, falling back to our high-fidelity generators.
- **IP Clustering:** Standard cloud container hosting IP pools can trigger captchas faster than residential connections.

### Future Roadmap:
- **API Grounding / Playwright Integration:** Optionally add a Playwright toggle for headless browser rendering.
- **Multi-Currency Support:** Integrate an automated exchange-rate API to support multi-currency listings.
- **Product Image Generation:** Connect Gemini Image Generation (`gemini-3.1-flash-image`) to draft custom visual hero mockups based on the newly generated title.
