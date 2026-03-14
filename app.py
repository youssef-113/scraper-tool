"""
AI Web Scraper Pro - Combined Application
Features:
- Existing: Web Scraper, Power Analysis, RAG Data Analyzer with Groq
- NEW: Gemini Live Agent for multimodal voice-interactive scraping
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import time
from io import BytesIO
import json
import asyncio
import base64

# Existing imports
from scraper import (
    ScrapingEngine,
    fetch_page_multi_engine,
    analyze_structure_advanced,
    extract_data_robust,
    clean_data_advanced,
    PowerScraper,
    analyze_page_structure
)
from scraper.structure_ai import generate_fallback_selectors
from analysis import calculate_comprehensive_kpis, generate_comprehensive_insights
from utils import (
    validate_url,
    parse_fields,
    estimate_scraping_time,
    check_robots_txt,
    sanitize_filename,
    extract_domain
)
from rag_analyzer import (
    DocumentProcessor,
    VectorStoreManager,
    ChatEngine,
    ProductExtractor
)

# NEW: Gemini Agent imports
from agent import GeminiScraperAgent, MultimodalHandler, ScraperTools, ConversationManager

load_dotenv()

st.set_page_config(
    page_title="AI Web Scraper Pro + Gemini Live Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    # Existing session states
    if 'scraping_results' not in st.session_state:
        st.session_state.scraping_results = None
    if 'kpis' not in st.session_state:
        st.session_state.kpis = None
    if 'insights' not in st.session_state:
        st.session_state.insights = None
    if 'structure_analysis' not in st.session_state:
        st.session_state.structure_analysis = None
    
    # RAG Analyzer session state
    if 'uploaded_df' not in st.session_state:
        st.session_state.uploaded_df = None
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'chat_engine' not in st.session_state:
        st.session_state.chat_engine = None
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'data_summary' not in st.session_state:
        st.session_state.data_summary = None
    if 'current_model' not in st.session_state:
        st.session_state.current_model = "llama-3.3-70b-versatile"
    
    # NEW: Gemini Agent session state
    if 'gemini_agent' not in st.session_state:
        st.session_state.gemini_agent = None
    if 'gemini_session_active' not in st.session_state:
        st.session_state.gemini_session_active = False
    if 'conversation_manager' not in st.session_state:
        st.session_state.conversation_manager = ConversationManager()
    if 'scraper_tools' not in st.session_state:
        st.session_state.scraper_tools = ScraperTools()
    if 'multimodal_handler' not in st.session_state:
        st.session_state.multimodal_handler = MultimodalHandler()
    if 'gemini_chat_history' not in st.session_state:
        st.session_state.gemini_chat_history = []

# ============================================================================
# GEMINI LIVE AGENT FUNCTIONS
# ============================================================================

def init_gemini_agent():
    """Initialize Gemini agent"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    return GeminiScraperAgent(api_key=api_key)

def render_gemini_agent_tab():
    """Render the Gemini Live Agent interface"""
    st.header("🤖 Gemini Live Agent")
    st.markdown("**First live voice agent for web scraping - Multimodal: Voice → Visual → Data**")
    
    # Check API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key:
        st.warning("⚠️ Google API Key not configured")
        st.info("""
        **How to get Google API Key:**
        1. Visit https://aistudio.google.com
        2. Sign up for free account
        3. Go to API Keys section
        4. Create new API key
        5. Add it as environment variable `GOOGLE_API_KEY`
        
        **Gemini 2.0 Flash supports multimodal + live interactions!** ⚡
        """)
        return
    
    # Session controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if not st.session_state.gemini_session_active:
            if st.button("🟢 Start Live Session", type="primary"):
                with st.spinner("Starting Gemini Live..."):
                    st.session_state.gemini_agent = init_gemini_agent()
                    if st.session_state.gemini_agent:
                        success = st.session_state.gemini_agent.start_session()
                        st.session_state.gemini_session_active = success
                        if success:
                            st.success("✅ Live session active!")
                            st.rerun()
        else:
            st.success("🟢 Live session active")
    
    with col2:
        if st.session_state.gemini_session_active:
            if st.button("🔴 End Session"):
                if st.session_state.gemini_agent:
                    farewell = st.session_state.gemini_agent.close_session()
                    st.info(f"👋 {farewell}")
                st.session_state.gemini_session_active = False
                st.rerun()
    
    with col3:
        if st.session_state.gemini_session_active:
            st.metric("Messages", len(st.session_state.gemini_chat_history))
    
    if not st.session_state.gemini_session_active:
        st.markdown("---")
        st.markdown("### 📖 Quick Start Guide")
        st.markdown("""
        **How to Use Gemini Scraper Agent:**
        
        1. **Start Live Session** (button above)
        2. **Enter URL** to scrape
        3. **Type or use voice** for instructions
        4. **Interrupt anytime** to adjust strategy
        5. **Get results** in real-time
        
        **Voice Commands Examples:**
        - "Extract all product names"
        - "Show me the prices"
        - "Wait, change strategy"
        - "How many items found?"
        
        **Multimodal Capabilities:**
        - 📸 Screenshot analysis
        - 🎙️ Voice interaction
        - 👁️ Visual structure detection
        """)
        return
    
    # Active session interface
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Interactive Scrape", "💬 Chat", "👁️ Visual Analysis", "📊 Results"])
    
    with tab1:
        st.subheader("Interactive Scraping")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            url = st.text_input(
                "🌐 Target URL",
                placeholder="https://example.com/products"
            )
        
        with col2:
            scrape_mode = st.selectbox(
                "Mode",
                ["⌨️ Text", "🎙️ Voice", "👁️ Visual"]
            )
        
        # Instructions based on mode
        if scrape_mode == "⌨️ Text":
            instructions = st.text_area(
                "Instructions for Agent",
                placeholder="Extract product names, prices, and ratings...",
                height=100
            )
        elif scrape_mode == "🎙️ Voice":
            st.info("🎤 Voice mode: Click 'Start Scraping' then speak your instructions")
            instructions = "Use voice input"
        else:
            st.info("📸 Visual mode: Agent will analyze webpage screenshots")
            instructions = st.text_input("What should I look for?")
        
        # Scraping controls
        col_start, col_interrupt = st.columns([1, 1])
        
        with col_start:
            if st.button("🚀 Start Scraping", type="primary", disabled=not url):
                with st.spinner("🤖 Agent is working..."):
                    result = st.session_state.gemini_agent.interactive_scraping(
                        url=url,
                        user_instructions=instructions or "Extract all visible data",
                        progress_callback=lambda msg: st.info(msg)
                    )
                    st.success(f"✅ {result['agent_response']}")
                    st.session_state.gemini_chat_history.append({
                        'role': 'agent',
                        'content': result['agent_response'],
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
        
        with col_interrupt:
            interrupt_msg = st.text_input(
                "Send interruption",
                placeholder="Wait! Also extract the descriptions..."
            )
            if st.button("📨 Send Interruption") and interrupt_msg:
                response = st.session_state.gemini_agent.handle_interruption(interrupt_msg)
                st.info(f"🤖 Agent: {response}")
                st.session_state.gemini_chat_history.append({
                    'role': 'user',
                    'content': interrupt_msg,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                st.session_state.gemini_chat_history.append({
                    'role': 'agent',
                    'content': response,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
    
    with tab2:
        st.subheader("💬 Chat with Agent")
        
        # Chat history display
        if st.session_state.gemini_chat_history:
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.gemini_chat_history[-10:]:
                    role_icon = "🤖" if chat['role'] == 'agent' else "🙋"
                    with st.chat_message("assistant" if chat['role'] == 'agent' else "user"):
                        st.markdown(f"**{role_icon}** ({chat['timestamp']}): {chat['content']}")
        
        # Chat input
        user_message = st.chat_input("Ask the agent anything...")
        
        if user_message:
            with st.chat_message("user"):
                st.write(user_message)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.gemini_agent.chat(user_message)
                    st.write(response)
            
            st.session_state.gemini_chat_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            st.session_state.gemini_chat_history.append({
                'role': 'agent',
                'content': response,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()
    
    with tab3:
        st.subheader("👁️ Visual Analysis")
        
        # Screenshot upload
        uploaded_image = st.file_uploader(
            "📸 Upload webpage screenshot",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a screenshot for visual analysis"
        )
        
        question = st.text_input(
            "What do you want to know about this page?",
            placeholder="What data can be extracted?"
        )
        
        if uploaded_image and question:
            if st.button("🔍 Analyze Screenshot", type="primary"):
                with st.spinner("Analyzing..."):
                    image_data = uploaded_image.read()
                    
                    # Analyze with Gemini
                    result = st.session_state.gemini_agent.analyze_screenshot(
                        image_data, question
                    )
                    
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.success("✅ Analysis complete!")
                        
                        # Display results
                        if 'structure' in result:
                            st.markdown("#### 🏗️ Structure")
                            st.json(result['structure'])
                        
                        if 'patterns' in result:
                            st.markdown("#### 📊 Patterns")
                            st.json(result['patterns'])
                        
                        if 'selectors' in result:
                            st.markdown("#### 🎯 Suggested Selectors")
                            st.json(result['selectors'])
                        
                        if 'strategy' in result:
                            st.markdown("#### 📋 Strategy")
                            st.write(result['strategy'])
                        
                        if 'analysis' in result:
                            st.markdown("#### 📝 Analysis")
                            st.write(result['analysis'])
    
    with tab4:
        st.subheader("📊 Scraping Results")
        
        if st.session_state.scraping_results is not None:
            df = st.session_state.scraping_results
            
            # AI Summary
            if st.button("🤖 Get AI Summary"):
                with st.spinner("Generating summary..."):
                    summary = st.session_state.gemini_agent.generate_summary(
                        df.to_dict('records')
                    )
                    st.info(summary)
            
            # Data display
            st.dataframe(df, use_container_width=True)
            
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                data=csv,
                file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data scraped yet. Start a scraping session!")

# ============================================================================
# EXISTING RAG CHAT INTERFACE
# ============================================================================

def render_chat_interface(groq_api_key: str):
    """Render the enhanced chat interface with Groq"""
    
    st.subheader("💬 Chat with Your Data (Powered by Groq)")
    
    if not groq_api_key:
        st.warning("⚠️ Groq API Key not configured")
        st.info("""
        **How to get Groq API Key:**
        1. Visit https://console.groq.com
        2. Sign up for free account
        3. Go to API Keys section
        4. Create new API key
        5. Add it as environment variable `GROQ_API_KEY`
        
        **Groq is FREE and MUCH FASTER than OpenAI!** ⚡
        """)
        return
    
    # Model selection
    col_model, col_temp = st.columns([2, 1])
    
    with col_model:
        available_models = {
            "Llama 3.3 70B (Best Quality)": "llama-3.3-70b-versatile",
            "Llama 3.1 70B (Balanced)": "llama-3.1-70b-versatile",
            "Llama 3.1 8B (Fastest)": "llama-3.1-8b-instant",
            "Mixtral 8x7B (Creative)": "mixtral-8x7b-32768",
            "Gemma 2 9B (Efficient)": "gemma2-9b-it"
        }
        
        selected_model_name = st.selectbox(
            "Select AI Model:",
            list(available_models.keys()),
            index=0,
            help="Different models offer different speeds and capabilities"
        )
        
        selected_model = available_models[selected_model_name]
        
        if selected_model != st.session_state.current_model:
            st.session_state.current_model = selected_model
            if st.session_state.chat_engine:
                st.session_state.chat_engine.change_model(selected_model)
    
    with col_temp:
        st.metric("Speed", "⚡ Ultra Fast" if "instant" in selected_model else "🚀 Fast")
    
    # Example questions
    with st.expander("💡 Example Questions You Can Ask", expanded=False):
        example_cols = st.columns(2)
        
        with example_cols[0]:
            st.markdown("""
            **Basic Analysis:**
            - What is the average price?
            - How many products do we have?
            - Show me the most expensive items
            - What categories are available?
            - How many unique brands exist?
            """)
        
        with example_cols[1]:
            st.markdown("""
            **Advanced Queries:**
            - Compare prices across categories
            - What's the price range for electronics?
            - Show products rated above 4.5 stars
            - Which brand has the highest average price?
            - Summarize the top 10 products by rating
            """)
    
    st.markdown("---")
    
    # Chat input
    user_question = st.text_input(
        "💭 Ask me anything about your data:",
        placeholder="e.g., What are the top 5 products by price?",
        key="chat_input"
    )
    
    col_ask, col_clear, col_export = st.columns([2, 1, 1])
    
    with col_ask:
        ask_button = st.button("🔍 Ask Question", type="primary")
    
    with col_clear:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            if st.session_state.chat_engine:
                st.session_state.chat_engine.clear_history()
            st.rerun()
    
    with col_export:
        if st.session_state.chat_history:
            chat_export = "\n\n".join([
                f"Q: {chat['question']}\nA: {chat['answer']}\n---"
                for chat in st.session_state.chat_history
            ])
            st.download_button(
                "💾 Export Chat",
                data=chat_export,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Process question
    if ask_button and user_question:
        with st.spinner("🤔 Analyzing your question..."):
            start_time = time.time()
            
            answer = st.session_state.chat_engine.query(
                user_question,
                st.session_state.data_summary,
                max_context_chunks=5,
                temperature=0.3
            )
            
            response_time = time.time() - start_time
            
            st.session_state.chat_history.append({
                'question': user_question,
                'answer': answer,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'response_time': response_time,
                'model': selected_model_name
            })
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 💬 Conversation History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.container():
                # Question
                st.markdown(f"""
                <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <strong>🙋 You ({chat['timestamp']})</strong><br>
                    {chat['question']}
                </div>
                """, unsafe_allow_html=True)
                
                # Answer
                st.markdown(f"""
                <div style='background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                    <strong>🤖 AI Assistant</strong> 
                    <span style='color: #666; font-size: 0.8em;'>
                        ({chat.get('model', 'Unknown')} • {chat.get('response_time', 0):.2f}s)
                    </span><br><br>
                    {chat['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.info("👆 Ask a question above to start chatting with your data!")

def render_rag_analyzer_tab(groq_api_key: str, openai_api_key: str = None):
    """Render the RAG Data Analyzer tab with Groq chatbot"""
    
    st.header("📊 RAG Data Analyzer with AI Chatbot")
    st.markdown("**Upload your data and chat with it using powerful Groq AI models**")
    
    st.markdown("---")
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "📁 Upload your data file (CSV or Excel)",
            type=['csv', 'xlsx', 'xls'],
            help="Upload product data, scraped results, or any tabular data"
        )
    
    with col2:
        if uploaded_file:
            st.success(f"✅ File loaded: {uploaded_file.name}")
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
    
    if uploaded_file:
        try:
            # Load and process the file
            if st.session_state.uploaded_df is None or uploaded_file.name != st.session_state.get('last_uploaded_file', ''):
                with st.spinner("🔄 Processing file and creating vector embeddings..."):
                    df = st.session_state.doc_processor.load_file(uploaded_file)
                    st.session_state.uploaded_df = df
                    st.session_state.last_uploaded_file = uploaded_file.name
                    
                    # Analyze DataFrame
                    analysis = st.session_state.doc_processor.analyze_dataframe(df)
                    summary = st.session_state.doc_processor.generate_summary(df)
                    st.session_state.data_summary = summary
                    st.session_state.data_analysis = analysis
                    
                    # Create chunks for vector store
                    chunks = st.session_state.doc_processor.create_document_chunks(df, chunk_size=10)
                    
                    # Initialize vector store
                    vector_store = VectorStoreManager(
                        openai_key=openai_api_key,
                        groq_key=groq_api_key
                    )
                    vector_store.add_documents(chunks)
                    st.session_state.vector_store = vector_store
                    
                    # Initialize chat engine with Groq
                    if groq_api_key:
                        st.session_state.chat_engine = ChatEngine(
                            groq_api_key,
                            vector_store,
                            model=st.session_state.current_model
                        )
                    
                    st.success("✅ File processed and ready for chat!")
            
            df = st.session_state.uploaded_df
            
            # Create tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "💬 AI Chatbot",
                "📊 Overview",
                "📦 Product Analysis",
                "📈 Statistics",
                "🔍 Data Explorer"
            ])
            
            with tab1:
                render_chat_interface(groq_api_key)
            
            with tab2:
                st.subheader("📊 Dataset Overview")
                
                # Basic metrics
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("Total Rows", f"{len(df):,}")
                with metric_cols[1]:
                    st.metric("Total Columns", len(df.columns))
                with metric_cols[2]:
                    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
                    st.metric("Memory Usage", f"{memory_mb:.2f} MB")
                with metric_cols[3]:
                    missing_pct = (df.isnull().sum().sum() / df.size * 100)
                    st.metric("Missing Data", f"{missing_pct:.1f}%")
                
                # Data summary
                st.markdown("#### 📋 Dataset Summary")
                if st.session_state.data_summary:
                    st.text(st.session_state.data_summary)
                
                # Column info
                st.markdown("#### 📑 Column Information")
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.values,
                    'Non-Null': df.count().values,
                    'Null': df.isnull().sum().values,
                    'Unique': [df[col].nunique() for col in df.columns]
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)
                
                # Sample data
                st.markdown("#### 🔍 Sample Data (First 10 rows)")
                st.dataframe(df.head(10), use_container_width=True, height=400)
            
            with tab3:
                st.subheader("📦 Product Analysis")
                
                product_extractor = ProductExtractor(df)
                
                # Product summary
                st.markdown("#### 📊 Product Summary")
                product_summary = product_extractor.generate_product_summary()
                st.text(product_summary)
                
                # Price distribution
                price_stats = product_extractor.extract_price_stats()
                if price_stats:
                    st.markdown("#### 💰 Price Distribution")
                    price_cols = st.columns(4)
                    with price_cols[0]:
                        st.metric("Minimum", f"${price_stats['min_price']:.2f}")
                    with price_cols[1]:
                        st.metric("Average", f"${price_stats['avg_price']:.2f}")
                    with price_cols[2]:
                        st.metric("Median", f"${price_stats['median_price']:.2f}")
                    with price_cols[3]:
                        st.metric("Maximum", f"${price_stats['max_price']:.2f}")
                
                # Category breakdown
                categories = product_extractor.extract_category_breakdown()
                if categories:
                    st.markdown("#### 📂 Category Breakdown")
                    cat_df = pd.DataFrame([
                        {'Category': cat, 'Count': count, 'Percentage': f"{count/len(df)*100:.1f}%"}
                        for cat, count in list(categories.items())[:20]
                    ])
                    st.dataframe(cat_df, use_container_width=True, hide_index=True)
                
                # Top products
                st.markdown("#### 🏆 Top Products by Price")
                top_products = product_extractor.get_top_products(by='price', limit=10)
                st.dataframe(top_products, use_container_width=True)
            
            with tab4:
                st.subheader("📈 Statistical Analysis")
                
                # Numeric statistics
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.markdown("#### 🔢 Numeric Columns Statistics")
                    st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
                # Categorical analysis
                text_cols = df.select_dtypes(include=['object']).columns
                if len(text_cols) > 0:
                    st.markdown("#### 📝 Categorical Analysis")
                    selected_cat = st.selectbox("Select column to analyze:", text_cols)
                    
                    if selected_cat:
                        value_counts = df[selected_cat].value_counts().head(20)
                        
                        col_chart, col_table = st.columns([2, 1])
                        
                        with col_chart:
                            st.bar_chart(value_counts)
                        
                        with col_table:
                            st.dataframe(
                                pd.DataFrame({
                                    'Value': value_counts.index,
                                    'Count': value_counts.values
                                }),
                                use_container_width=True,
                                hide_index=True,
                                height=400
                            )
                
                # Missing data
                st.markdown("#### ❌ Missing Data Analysis")
                missing_data = df.isnull().sum()
                if missing_data.sum() > 0:
                    missing_df = pd.DataFrame({
                        'Column': missing_data.index,
                        'Missing Count': missing_data.values,
                        'Percentage': (missing_data.values / len(df) * 100).round(2)
                    })
                    st.dataframe(
                        missing_df[missing_df['Missing Count'] > 0],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("✅ No missing data detected!")
            
            with tab5:
                st.subheader("🔍 Advanced Data Explorer")
                
                # Search functionality
                st.markdown("#### 🔎 Search")
                search_query = st.text_input("Search across all text columns:", placeholder="Enter search term...")
                
                if search_query:
                    mask = pd.Series([False] * len(df))
                    text_cols = df.select_dtypes(include=['object']).columns
                    
                    for col in text_cols:
                        mask |= df[col].astype(str).str.contains(search_query, case=False, na=False)
                    
                    search_results = df[mask]
                    st.markdown(f"**Found {len(search_results)} matching rows**")
                    st.dataframe(search_results, use_container_width=True, height=400)
                
                # Filtering
                st.markdown("#### 🎛️ Filter Data")
                filter_col = st.selectbox("Select column to filter:", df.columns)
                
                if filter_col:
                    col_type = df[filter_col].dtype
                    
                    if col_type in ['int64', 'float64']:
                        min_val = float(df[filter_col].min())
                        max_val = float(df[filter_col].max())
                        
                        range_vals = st.slider(
                            f"Select range for {filter_col}:",
                            min_val, max_val, (min_val, max_val)
                        )
                        
                        filtered_df = df[
                            (df[filter_col] >= range_vals[0]) &
                            (df[filter_col] <= range_vals[1])
                        ]
                    else:
                        unique_vals = df[filter_col].unique()[:100]
                        selected_vals = st.multiselect(
                            f"Select values for {filter_col}:",
                            unique_vals,
                            default=list(unique_vals[:5])
                        )
                        
                        if selected_vals:
                            filtered_df = df[df[filter_col].isin(selected_vals)]
                        else:
                            filtered_df = df
                    
                    st.markdown(f"**Filtered Results: {len(filtered_df):,} rows**")
                    st.dataframe(filtered_df, use_container_width=True, height=400)
                    
                    # Download filtered
                    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Filtered Data",
                        data=csv_data,
                        file_name=f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    init_session_state()
    
    st.title("🤖 AI Web Scraper Pro + Gemini Live Agent")
    st.markdown("**Professional web scraping + AI-powered data chat with Groq + Multimodal Voice Agent**")
    
    # Load API keys from environment
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    
    # Sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🛠️ Scraping Engine")
        
        engine_options = {
            "AUTO (Recommended)": ScrapingEngine.AUTO,
            "Scrapling (Fast)": ScrapingEngine.SCRAPLING,
            "Playwright (JS Sites)": ScrapingEngine.PLAYWRIGHT,
            "Selenium (Compatible)": ScrapingEngine.SELENIUM
        }
        
        selected_engine = st.selectbox(
            "Select Engine",
            options=list(engine_options.keys()),
            index=0
        )
        
        engine = engine_options[selected_engine]
        
        st.markdown("---")
        st.subheader("⚡ Settings")
        
        timeout = st.slider("Timeout (sec)", 10, 120, 30, 5)
        delay = st.slider("Delay (sec)", 0.0, 5.0, 1.0, 0.5)
        max_items = st.number_input("Max Items", 10, 10000, 500, 50)
        
        # API Status
        st.markdown("---")
        st.subheader("🔑 API Status")
        
        if google_api_key:
            st.success("✅ Google (Gemini)")
        else:
            st.warning("⚠️ Google (Gemini) - Not set")
        
        if groq_api_key:
            st.success("✅ Groq")
        else:
            st.warning("⚠️ Groq - Not set")
        
        if openai_api_key:
            st.success("✅ OpenAI")
        else:
            st.info("ℹ️ OpenAI - Optional")
    
    # Main navigation
    main_tab = st.radio(
        "Select Feature:",
        ["🤖 Gemini Live Agent", "📊 RAG Data Analyzer", "🚀 Web Scraper", "🔬 Power Analysis"],
        horizontal=True
    )
    
    if main_tab == "🤖 Gemini Live Agent":
        render_gemini_agent_tab()
    
    elif main_tab == "📊 RAG Data Analyzer":
        render_rag_analyzer_tab(groq_api_key, openai_api_key)
    
    elif main_tab == "🚀 Web Scraper":
        st.markdown("---")
        st.header("🚀 Web Scraper")
        st.info("Web scraping functionality - enter URLs and fields to scrape")
        
        col1, col2 = st.columns([1.2, 1])
        
        with col1:
            urls_input = st.text_area(
                "Website URLs (one per line)",
                height=120,
                placeholder="https://example.com/products"
            )
            
            fields_input = st.text_input(
                "Data Fields (comma-separated)",
                placeholder="title, price, rating"
            )
        
        with col2:
            if urls_input and fields_input:
                urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
                fields = parse_fields(fields_input)
                
                st.metric("URLs", len(urls))
                st.metric("Fields", len(fields))
        
        if st.button("🚀 Start Scraping", type="primary"):
            st.info("Scraping started... (Implementation continues here)")
    
    elif main_tab == "🔬 Power Analysis":
        st.markdown("---")
        st.header("🔬 Power Analysis Mode")
        
        analysis_url = st.text_input("URL to Analyze", placeholder="https://example.com/products")
        
        if st.button("🔍 Analyze Structure", type="primary"):
            if not analysis_url or not validate_url(analysis_url):
                st.error("Invalid URL")
            else:
                with st.spinner("Fetching page..."):
                    html, engine_used, success = fetch_page_multi_engine(analysis_url, engine, timeout, delay)
                
                if not html or not success:
                    st.error("Failed to fetch page")
                else:
                    st.success(f"✅ Page fetched using {engine_used}")
                    
                    # Analyze structure
                    analysis = analyze_page_structure(html)
                    
                    st.subheader("📊 Structure Analysis")
                    st.json(analysis)
    
    # Footer
    st.markdown("---")
    st.caption("Powered by Gemini 2.0 Flash + Groq Llama 3 • Deployed on Google Cloud Run • Built for #GeminiLiveAgentChallenge")

if __name__ == "__main__":
    main()
