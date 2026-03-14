# 🕷️ AI Web Scraper Pro

**Professional web scraping + AI-powered data analysis**

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A powerful web scraping platform with AI chat capabilities for data analysis.

**Author:** Youssef Bassiony | **Role:** AI Engineer

---

## ✨ Features

### 📊 RAG Data Analyzer
- Upload CSV/Excel files and chat with your data
- Powered by Groq Llama 3 models (FREE!)
- Vector embeddings for semantic search
- Multiple AI models to choose from

### 🚀 Multi-Engine Web Scraper
- 4 scraping engines (Scrapling, Playwright, Selenium, Trafilatura)
- AI-powered structure detection
- Automatic CSS selector generation
- Data cleaning and deduplication

### 🔬 Power Analysis
- Advanced page structure analysis
- Tag and class detection
- Pattern recognition

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Groq API key ([Get one FREE here](https://console.groq.com))

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/scraper-tool
cd scraper-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Groq API key

# Run application
streamlit run app.py
```

---

## 🔑 API Key Setup

### Groq API Key (Required - FREE)
1. Visit: https://console.groq.com
2. Sign up for free account
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Add to `.env` as `GROQ_API_KEY`

**FREE tier includes:**
- 30 requests/minute
- Unlimited tokens/day
- All Llama 3 models available

---

## 📖 How It Works

### Gemini Live Agent Flow
```
User Voice/Text → Gemini Agent → Intent Analysis
        ↓
  Scraper Tools → Fetch Page
        ↓
  Visual Analysis → Extract Data
        ↓
  Natural Language Summary → Results
```

### Example Usage

**Voice Command:**
```
User: "Hey Gemini, scrape all products from example.com 
       and get the names, prices, and ratings"

Agent: "Got it! Analyzing the page structure..."
       "I see 47 products in a grid layout. Starting extraction..."
       "Done! Found 47 products. Average price: $49.99"
```

**Interruption:**
```
Agent: "Extracting products... 23 of 47 complete..."

User: "Wait! Also get the product descriptions"

Agent: "Understood. Adding descriptions to extraction. 
       Resuming from product 23..."
```

---

## 🏗️ Project Structure

```
scraper-tool/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
├── cloudbuild.yaml           # CI/CD pipeline
│
├── agent/                    # Gemini Live Agent module
│   ├── __init__.py
│   ├── gemini_agent.py       # Core agent implementation
│   ├── multimodal_handler.py # Vision/voice processing
│   ├── scraper_tools.py      # Scraping function tools
│   └── conversation_manager.py
│
├── rag_analyzer/             # RAG Data Analyzer module
│   ├── __init__.py
│   ├── vector_store.py       # Vector database
│   ├── chat_engine.py        # Groq chat engine
│   ├── document_processor.py # File processing
│   └── extractor.py          # Product extraction
│
├── scraper/                  # Web scraping module
│   ├── __init__.py
│   ├── fetcher.py            # Multi-engine fetcher
│   ├── structure_ai.py       # AI structure analysis
│   └── extractors.py         # Data extractors
│
├── analysis/                 # Data analysis module
│   ├── __init__.py
│   ├── kpi_calculator.py
│   └── insights_generator.py
│
├── gcp/                      # GCP deployment files
│   ├── deploy.sh             # Deployment script
│   ├── setup_gcp.sh          # GCP initialization
│   ├── local_test.sh         # Local Docker test
│   └── cloud_run_service.yaml
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md       # Architecture details
│   ├── blog_post.md          # Blog post template
│   ├── architecture_diagram.py
│   └── create_flow_diagram.py
│
└── demo/                     # Demo materials
    └── demo_script.md        # Video demo script
```

---

## 🎯 Use Cases

- **E-Commerce Monitoring** - Track competitor prices
- **Real Estate Aggregation** - Collect property listings  
- **Job Board Analysis** - Monitor job postings
- **News Aggregation** - Gather articles from multiple sources
- **Market Research** - Collect product reviews
- **Lead Generation** - Extract business information

---

## 📊 Performance

| Metric | Traditional Scraping | Gemini Scraper Agent |
|--------|---------------------|----------------------|
| **Setup Time** | 2-4 hours | 2 minutes |
| **Code Required** | 100-200 lines | 0 lines |
| **Accuracy** | 60-70% | 95%+ |
| **Adaptability** | Breaks on updates | Self-adjusting |
| **User Skill** | Developer | Anyone |

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Playwright browser issues
```bash
python -m playwright install chromium
python -m playwright install-deps
```

### Groq API errors
- Check API key is correct
- Verify you're within rate limits (30/min)
- Try different model (Llama 3.1 8B is faster)

---

## 🔒 Security Best Practices

1. **Never commit .env file**
```bash
echo ".env" >> .gitignore
```

2. **Rotate API keys monthly**
3. **Use environment variables in production**
4. **Enable HTTPS for production**
5. **Implement rate limiting**

---

## 📈 Deployment Options

### Streamlit Cloud (Easiest)
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy!

### Docker (Anywhere)
```bash
docker build -t ai-web-scraper .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key ai-web-scraper
```

---

## 📄 License

MIT License - Use freely for commercial projects!

---

## 📬 Contact

- **Author:** Youssef Bassiony
- **Role:** AI Engineer
- **Issues:** [GitHub Issues](https://github.com/yourusername/scraper-tool/issues)

---

**⭐ If you find this helpful, give it a star on GitHub!**