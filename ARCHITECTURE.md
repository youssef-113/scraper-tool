# Architecture Documentation

## AI Web Scraper Pro + Gemini Live Agent

A comprehensive web scraping platform combining traditional scraping engines with AI-powered analysis and a live multimodal agent.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit Web UI                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│  │ Gemini Live  │ │ RAG Analyzer │ │ Web Scraper  │ │  Power     │ │
│  │    Agent     │ │   + Groq     │ │   Classic    │ │  Analysis  │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Core Modules                                 │
│                                                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │   agent/            │  │   rag_analyzer/     │                  │
│  │   ├── gemini_agent  │  │   ├── vector_store  │                  │
│  │   ├── multimodal    │  │   ├── chat_engine   │                  │
│  │   ├── scraper_tools │  │   ├── document_proc │                  │
│  │   └── conversation  │  │   └── extractor     │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │   scraper/         │  │   analysis/         │                  │
│  │   ├── fetcher      │  │   ├── kpi_calc      │                  │
│  │   ├── structure_ai │  │   ├── insights      │                  │
│  │   └── extractors   │  │   └── visualizer    │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External APIs                                   │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ Google      │  │ Groq        │  │ OpenAI      │                 │
│  │ Gemini 2.0  │  │ Llama 3     │  │ Embeddings  │                 │
│  │ Flash       │  │ Models      │  │ (Optional)  │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Gemini Live Agent (`agent/`)

The flagship feature - a live, conversational AI agent for web scraping.

**Files:**
- `gemini_agent.py` - Core agent implementation using Gemini 2.0 Flash
- `multimodal_handler.py` - Vision and voice input processing
- `scraper_tools.py` - Web scraping function tools for the agent
- `conversation_manager.py` - Session and context management

**Key Features:**
- Real-time voice interaction
- Screenshot analysis with vision models
- Interruptible scraping sessions
- Natural language data extraction
- Context-aware conversations

**API Flow:**
```
User Voice/Text → Gemini Agent → Intent Analysis
                    ↓
            Scraper Tools → Fetch Page
                    ↓
            Analyze Structure → Extract Data
                    ↓
            Return Results → Natural Language Summary
```

---

### 2. RAG Data Analyzer (`rag_analyzer/`)

AI-powered data analysis with vector embeddings and conversational querying.

**Files:**
- `vector_store.py` - Vector database management (OpenAI + fallback)
- `chat_engine.py` - Groq-powered conversational AI
- `document_processor.py` - File loading and chunking
- `extractor.py` - Product data extraction utilities

**Key Features:**
- Upload CSV/Excel files
- Vector embeddings for semantic search
- Chat with data using natural language
- Multiple Groq models (Llama 3.3 70B, Mixtral, Gemma)
- Fallback keyword search if no OpenAI key

**Data Flow:**
```
Upload File → Document Processor → Create Chunks
                                        ↓
                                Vector Store → Embeddings
                                        ↓
User Question → Chat Engine → Retrieve Context
                                        ↓
                                Groq API → Generate Answer
```

---

### 3. Web Scraper (`scraper/`)

Multi-engine web scraping with AI-powered structure analysis.

**Engines:**
- **Scrapling** - Fast, lightweight scraping
- **Playwright** - JavaScript-heavy sites
- **Selenium** - Maximum compatibility
- **Trafilatura** - Article/content extraction
- **AUTO** - Intelligent engine selection

**Key Features:**
- Automatic structure detection
- AI-generated CSS selectors
- Robust data extraction
- Data cleaning and deduplication
- Export to CSV/JSON

---

### 4. Analysis Module (`analysis/`)

Comprehensive data analysis and insights generation.

**Features:**
- KPI calculations
- Statistical analysis
- Trend detection
- Automated insights
- Visualization helpers

---

## Deployment Architecture

### Streamlit Cloud (Primary)

```
GitHub Repository → Streamlit Cloud → Auto Deploy
                            ↓
                    Load Environment Variables
                            ↓
                    Run Streamlit App (Port 8501)
```

**Configuration:**
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit settings
- Environment variables via Streamlit Cloud dashboard

---

### Google Cloud Run (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                     │
│                                                              │
│  ┌────────────────┐    ┌────────────────┐                  │
│  │ Cloud Build    │───▶│ Container Reg  │                  │
│  │ (CI/CD)        │    │ (Docker Image) │                  │
│  └────────────────┘    └────────────────┘                  │
│           │                     │                           │
│           ▼                     ▼                           │
│  ┌────────────────┐    ┌────────────────┐                  │
│  │ cloudbuild.yaml│    │  Cloud Run     │                  │
│  │ Dockerfile     │    │  Service       │                  │
│  └────────────────┘    └────────────────┘                  │
│                              │                              │
│                              ▼                              │
│                    ┌────────────────┐                       │
│                    │ Secret Manager │                       │
│                    │ (API Keys)     │                       │
│                    └────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Deployment Files:**
- `Dockerfile` - Container image definition
- `cloudbuild.yaml` - CI/CD pipeline
- `gcp/deploy.sh` - Deployment script
- `gcp/setup_gcp.sh` - Environment setup
- `gcp/cloud_run_service.yaml` - Service configuration

**Resource Allocation:**
- Memory: 2GB
- CPU: 2 cores
- Timeout: 300 seconds
- Max Instances: 10
- Min Instances: 1

---

## API Keys & Environment Variables

### Required

| Variable | Description | Get From |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Gemini 2.0 Flash access | [Google AI Studio](https://aistudio.google.com) |
| `GROQ_API_KEY` | Llama 3 models access | [Groq Console](https://console.groq.com) |

### Optional

| Variable | Description | Get From |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Vector embeddings | [OpenAI Platform](https://platform.openai.com) |

---

## Data Flow Diagrams

### Gemini Live Agent Flow

```
┌──────────┐    Voice/Text    ┌──────────────┐
│   User   │ ───────────────▶ │   Gemini     │
└──────────┘                  │   Agent      │
     ▲                        └──────────────┘
     │                               │
     │                         Intent Analysis
     │                               │
     │                               ▼
     │                        ┌──────────────┐
     │   Natural Language     │   Scraper    │
     ├◀────────────────────── │   Tools      │
     │      Summary           └──────────────┘
     │                               │
     │                               ▼
     │                        ┌──────────────┐
     └───────────────────────▶│   Extracted  │
              Results         │   Data       │
                              └──────────────┘
```

### RAG Chat Flow

```
┌──────────┐    Question     ┌──────────────┐
│   User   │ ─────────────▶ │   Chat       │
└──────────┘                 │   Engine     │
     ▲                       └──────────────┘
     │                              │
     │                        Retrieve Context
     │                              │
     │                              ▼
     │                       ┌──────────────┐
     │   AI Answer           │   Vector     │
     ├◀───────────────────── │   Store      │
     │                       └──────────────┘
     │                              │
     │                              ▼
     │                       ┌──────────────┐
     └──────────────────────▶│   Groq API   │
              Context         │   (Llama 3)  │
                              └──────────────┘
```

---

## Security Considerations

1. **API Keys**: Never hardcoded, loaded from environment variables
2. **Secret Manager**: GCP Secret Manager for production deployment
3. **Non-root User**: Docker container runs as unprivileged user
4. **No UI Key Inputs**: Removed from sidebar to prevent exposure
5. **Health Checks**: Container health monitoring

---

## Performance Optimization

1. **Vector Store Caching**: Embeddings cached in session state
2. **Model Selection**: Fast models (Llama 3.1 8B) for quick queries
3. **Chunking Strategy**: 10 records per chunk for optimal retrieval
4. **Lazy Loading**: Components loaded only when needed
5. **Connection Pooling**: HTTP connection reuse

---

## Future Enhancements

1. **Real Voice Integration**: WebRTC for live voice streaming
2. **Multi-language Support**: Internationalization
3. **Scheduled Scraping**: Cron-based automated scraping
4. **Export Formats**: Parquet, SQLite, API endpoints
5. **Collaborative Sessions**: Multi-user scraping sessions
6. **Custom Agent Training**: Fine-tuned models for specific domains

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Frontend | Streamlit |
| Backend | Python 3.11 |
| AI Models | Gemini 2.0 Flash, Groq Llama 3 |
| Vector DB | In-memory with FAISS fallback |
| Scraping | Scrapling, Playwright, Selenium |
| Deployment | Docker, Cloud Run, Streamlit Cloud |
| CI/CD | GitHub Actions, Cloud Build |

---

## Directory Structure

```
scraper-tool/
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
│   ├── deploy.sh
│   ├── setup_gcp.sh
│   └── cloud_run_service.yaml
│
├── .github/workflows/        # GitHub Actions
│   └── deploy.yml
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
├── cloudbuild.yaml           # CI/CD pipeline
├── README.md                 # Project documentation
└── ARCHITECTURE.md           # This file
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

---

## License

MIT License - See LICENSE file for details.
