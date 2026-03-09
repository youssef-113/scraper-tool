# AI Web Scraper Pro - Complete Installation Guide

## 📦 What You're Getting

Complete production-ready system with:
- ✅ Advanced web scraping (4 engines)
- ✅ AI structure detection (GPT-4)
- ✅ RAG data analyzer with Groq chatbot
- ✅ Professional PDF documentation
- ✅ Full source code

## 🚀 Quick Start (5 Minutes)

### Step 1: Extract Files
```bash
unzip ai_web_scraper_with_groq_chatbot.zip
cd ai_web_scraper
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
python setup_browsers.py
```

### Step 3: Configure API Keys
```bash
cp .env.example .env
nano .env  # Or use any text editor
```

Add your keys:
```
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Step 4: Run Application
```bash
streamlit run app.py
```

### Step 5: Generate Documentation
```bash
python create_project_pdf.py
```

## 🔑 Getting API Keys

### Groq API (FREE - Required for Chat)
1. Visit: https://console.groq.com
2. Sign up (free account)
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy and paste in .env file

**Cost**: FREE tier includes:
- 30 requests/minute
- Unlimited tokens/day
- All models available

### OpenAI API (Optional - For Structure Analysis)
1. Visit: https://platform.openai.com
2. Sign up / Login
3. Navigate to "API Keys"
4. Create new secret key
5. Copy and paste in .env file

**Cost**: Pay-as-you-go
- GPT-4: ~$0.03 per analysis
- Embeddings: ~$0.0001 per document
- Typical usage: $5-20/month

## 📊 Using the System

### Web Scraping
1. Select "🚀 Web Scraper" tab
2. Enter URLs (one per line)
3. Specify fields (e.g., "title, price, rating")
4. Click "Start Scraping"
5. View results and download CSV

### RAG Data Analyzer
1. Select "📊 RAG Data Analyzer" tab
2. Upload CSV/Excel file
3. Wait for processing
4. Navigate to "💬 AI Chatbot" sub-tab
5. Ask questions about your data!

### Example Questions:
```
"What is the average price?"
"Show me products above $100"
"How many categories exist?"
"Compare prices by brand"
"What's the most expensive item?"
```

## 🏗️ Project Structure
```
ai_web_scraper/
├── app.py                          # Main application
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── README.md                       # Documentation
├── setup_browsers.py               # Browser setup
├── create_project_pdf.py           # PDF generator
│
├── scraper/                        # Scraping module
│   ├── fetcher.py                 # Multi-engine fetcher
│   ├── structure_ai.py            # AI analyzer
│   ├── extractor.py               # Data extraction
│   ├── cleaner.py                 # Data cleaning
│   └── tag_class_analyzer.py      # Power analyzer
│
├── rag_analyzer/                   # RAG module
│   ├── document_processor.py      # File processing
│   ├── vector_store.py            # Embeddings
│   ├── chat_engine.py             # Groq chatbot
│   └── product_extractor.py       # Product analysis
│
├── analysis/                       # Analytics module
│   ├── kpi.py                     # KPI calculations
│   └── insights_ai.py             # AI insights
│
└── utils/                          # Utilities
    └── helpers.py                 # Helper functions
```

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

### OpenAI API errors
- Verify billing is set up
- Check API key is active
- Monitor usage dashboard

## 💡 Tips & Best Practices

### For Best Scraping Results:
1. Start with AUTO engine mode
2. Use specific field names
3. Respect robots.txt
4. Add delays between requests (1-2 seconds)
5. Test with 1 URL first

### For Best Chat Results:
1. Use Llama 3.3 70B for quality
2. Use Llama 3.1 8B for speed
3. Ask specific questions
4. Reference column names correctly
5. Request comparisons and analysis

### For Production Deployment:
1. Set up proper error logging
2. Implement rate limiting
3. Add user authentication
4. Enable HTTPS
5. Monitor API costs
6. Set up backups

## 📈 Performance Optimization

### Scraping Speed
- Use Scrapling for static sites (fastest)
- Use AUTO mode for auto-selection
- Reduce timeout for slow sites
- Enable concurrent requests (advanced)

### Chat Speed
- Llama 3.1 8B Instant: ~0.5s response
- Llama 3.3 70B: ~1-2s response
- Reduce context chunks if slow (5→3)
- Use smaller chunk sizes (10→5)

## 🔒 Security Best Practices

1. **Never commit .env file**
```bash
   echo ".env" >> .gitignore
```

2. **Rotate API keys monthly**
3. **Use environment variables in production**
4. **Enable HTTPS for production**
5. **Implement rate limiting**

## 📞 Support

### Issues?
- Check documentation first
- Review error messages
- Check API key validity
- Verify internet connection


## 📝 License

MIT License - Use freely for commercial projects!

## 🎉 You're Ready!

Start scraping and analyzing data with AI!
```bash
streamlit run app.py
```

Visit: http://localhost:8501