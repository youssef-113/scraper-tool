# AI-Powered Universal Web Scraper

A powerful, production-ready web scraping application that uses AI and advanced scraping techniques to extract data from ANY website structure.

## 🚀 Features

- **Universal Scraping**: Works with any website structure
- **AI-Driven Analysis**: Automatically detects data patterns using Groq Llama 3
- **Multi-Engine Support**:
  - Scrapling (primary engine - handles 95% of websites)
  - Playwright (JavaScript-heavy sites)
  - Selenium (fallback for complex sites)
  - Trafilatura (content extraction)
- **Smart Fallback System**: Automatically switches engines if one fails
- **Anti-Detection**: Rotating user agents, headers, delays
- **Robust Extraction**: Handles missing data, malformed HTML, dynamic content
- **Advanced Cleaning**: Deduplication, normalization, validation
- **Comprehensive Analysis**:
  - Statistical analysis
  - AI-generated insights
  - Data quality scoring
- **Professional Export**: CSV with metadata and timestamps
- **Error Recovery**: Automatic retry with different strategies

## 🛠️ Tech Stack

- **Streamlit**: Modern web interface
- **Scrapling**: Primary scraping engine
- **Playwright**: JavaScript rendering
- **Selenium**: Fallback for complex scenarios
- **BeautifulSoup4 + lxml**: HTML parsing
- **Trafilatura**: Content extraction
- **Groq (Llama 3)**: AI analysis
- **Pandas + NumPy**: Data processing

## 📦 Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install browsers:
```bash
python setup_browsers.py
```

4. Configure API key:
```bash
cp .env.example .env
```

5. Run:
```bash
streamlit run app.py
```

## ⚠️ Legal & Ethical Guidelines

Only scrape public data. Respect Terms of Service and robots.txt.
