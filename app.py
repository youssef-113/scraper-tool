"""
AI Web Scraper Pro
Features:
- Web Scraper with multiple engines
- RAG Data Analyzer with Groq AI Chat
- Power Analysis

Author: Youssef Bassiony - AI Engineer
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import time
from io import BytesIO
import json

# Scraper imports
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

load_dotenv()

st.set_page_config(
    page_title="AI Web Scraper Pro",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    # Scraping session states
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


# ============================================================================
# RAG CHAT INTERFACE
# ============================================================================

def render_chat_interface(groq_api_key: str):
    """Render the chat interface with Groq"""
    
    st.subheader("💬 Chat with Your Data")
    st.markdown("Powered by Groq AI - Fast & Free")
    
    if not groq_api_key:
        st.warning("⚠️ Groq API Key not configured")
        st.info("""
        **How to get Groq API Key (FREE):**
        1. Visit https://console.groq.com
        2. Sign up for free account
        3. Go to API Keys section
        4. Create new API key
        5. Add it to your .env file as `GROQ_API_KEY`
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
            index=0
        )
        
        selected_model = available_models[selected_model_name]
        
        if selected_model != st.session_state.current_model:
            st.session_state.current_model = selected_model
            if st.session_state.chat_engine:
                st.session_state.chat_engine.change_model(selected_model)
    
    with col_temp:
        st.metric("Speed", "Ultra Fast" if "instant" in selected_model else "Fast")
    
    # Example questions
    with st.expander("Example Questions", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - What is the average price?
            - How many products do we have?
            - Show me the most expensive items
            - What categories are available?
            """)
        
        with col2:
            st.markdown("""
            - Compare prices across categories
            - What's the price range?
            - Show products rated above 4.5
            - Summarize the top 10 products
            """)
    
    st.markdown("---")
    
    # Chat input
    user_question = st.text_input(
        "Ask me anything about your data:",
        placeholder="e.g., What are the top 5 products by price?",
        key="chat_input"
    )
    
    col_ask, col_clear, col_export = st.columns([2, 1, 1])
    
    with col_ask:
        ask_button = st.button("Ask Question", type="primary")
    
    with col_clear:
        if st.button("Clear Chat"):
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
                "Export Chat",
                data=chat_export,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Process question
    if ask_button and user_question:
        with st.spinner("Analyzing..."):
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
        st.markdown("### Conversation History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.container():
                st.markdown(f"""
                <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <strong>You ({chat['timestamp']})</strong><br>
                    {chat['question']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                    <strong>AI Assistant</strong> 
                    <span style='color: #666; font-size: 0.8em;'>
                        ({chat.get('model', 'Unknown')} • {chat.get('response_time', 0):.2f}s)
                    </span><br><br>
                    {chat['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.info("Ask a question above to start chatting with your data!")


def render_rag_analyzer_tab(groq_api_key: str):
    """Render the RAG Data Analyzer tab"""
    
    st.header("📊 RAG Data Analyzer")
    st.markdown("Upload your data and chat with it using AI")
    
    st.markdown("---")
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your data file (CSV or Excel)",
            type=['csv', 'xlsx', 'xls'],
            help="Upload product data, scraped results, or any tabular data"
        )
    
    with col2:
        if uploaded_file:
            st.success(f"File loaded: {uploaded_file.name}")
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
    
    if uploaded_file:
        try:
            # Load and process the file
            if st.session_state.uploaded_df is None or uploaded_file.name != st.session_state.get('last_uploaded_file', ''):
                with st.spinner("Processing file..."):
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
                    
                    # Initialize vector store (Groq only, no OpenAI)
                    vector_store = VectorStoreManager(
                        openai_key=None,
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
                    
                    st.success("File processed and ready!")
            
            df = st.session_state.uploaded_df
            
            # Create tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "💬 AI Chat",
                "📊 Overview",
                "📦 Product Analysis",
                "📈 Statistics",
                "🔍 Data Explorer"
            ])
            
            with tab1:
                render_chat_interface(groq_api_key)
            
            with tab2:
                st.subheader("Dataset Overview")
                
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
                st.markdown("#### Dataset Summary")
                if st.session_state.data_summary:
                    st.text(st.session_state.data_summary)
                
                # Column info
                st.markdown("#### Column Information")
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.values,
                    'Non-Null': df.count().values,
                    'Null': df.isnull().sum().values,
                    'Unique': [df[col].nunique() for col in df.columns]
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)
                
                # Sample data
                st.markdown("#### Sample Data (First 10 rows)")
                st.dataframe(df.head(10), use_container_width=True, height=400)
            
            with tab3:
                st.subheader("Product Analysis")
                
                product_extractor = ProductExtractor(df)
                
                # Product summary
                st.markdown("#### Product Summary")
                product_summary = product_extractor.generate_product_summary()
                st.text(product_summary)
                
                # Price distribution
                price_stats = product_extractor.extract_price_stats()
                if price_stats:
                    st.markdown("#### Price Distribution")
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
                    st.markdown("#### Category Breakdown")
                    cat_df = pd.DataFrame([
                        {'Category': cat, 'Count': count, 'Percentage': f"{count/len(df)*100:.1f}%"}
                        for cat, count in list(categories.items())[:20]
                    ])
                    st.dataframe(cat_df, use_container_width=True, hide_index=True)
                
                # Top products
                st.markdown("#### Top Products by Price")
                top_products = product_extractor.get_top_products(by='price', limit=10)
                st.dataframe(top_products, use_container_width=True)
            
            with tab4:
                st.subheader("Statistical Analysis")
                
                # Numeric statistics
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.markdown("#### Numeric Columns Statistics")
                    st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
                # Categorical analysis
                text_cols = df.select_dtypes(include=['object']).columns
                if len(text_cols) > 0:
                    st.markdown("#### Categorical Analysis")
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
                st.markdown("#### Missing Data Analysis")
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
                    st.success("No missing data detected!")
            
            with tab5:
                st.subheader("Advanced Data Explorer")
                
                # Search functionality
                st.markdown("#### Search")
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
                st.markdown("#### Filter Data")
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
                        label="Download Filtered Data",
                        data=csv_data,
                        file_name=f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    init_session_state()
    
    st.title("🕷️ AI Web Scraper Pro")
    st.markdown("**Professional web scraping + AI-powered data analysis**")
    
    # Load API key from environment
    
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
        st.subheader("API Status")
        
        if groq_api_key:
            st.success("Groq API: Connected")
        else:
            st.warning("Groq API: Not set")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("**Author:** Youssef Bassiony")
        st.markdown("**Role:** AI Engineer")
        st.markdown("---")
    
    # Main navigation
    main_tab = st.radio(
        "Select Feature:",
        ["📊 RAG Data Analyzer", "🚀 Web Scraper", "🔬 Power Analysis"],
        horizontal=True
    )
    
    if main_tab == "📊 RAG Data Analyzer":
        render_rag_analyzer_tab(groq_api_key)
    
    elif main_tab == "🚀 Web Scraper":
        st.markdown("---")
        st.header("🚀 Web Scraper")
        st.info("Enter URLs and fields to scrape data from websites")
        
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
        
        if st.button("Start Scraping", type="primary"):
            if not urls_input or not fields_input:
                st.error("Please enter URLs and fields")
            else:
                urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
                fields = parse_fields(fields_input)
                
                all_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, url in enumerate(urls):
                    status_text.text(f"Scraping {i+1}/{len(urls)}: {url}")
                    
                    # Fetch page
                    html, engine_used, success = fetch_page_multi_engine(
                        url, engine, timeout, delay
                    )
                    
                    if success and html:
                        # Analyze structure
                        structure = analyze_structure_advanced(html)
                        
                        # Extract data
                        results = extract_data_robust(
                            html, fields, structure, max_items
                        )
                        
                        # Clean data
                        if results:
                            cleaned = clean_data_advanced(results)
                            all_results.extend(cleaned)
                    
                    progress_bar.progress((i + 1) / len(urls))
                
                status_text.text("Done!")
                
                if all_results:
                    df = pd.DataFrame(all_results)
                    st.session_state.scraping_results = df
                    
                    st.success(f"Extracted {len(df)} records!")
                    st.dataframe(df, use_container_width=True)
                    
                    # Download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download CSV",
                        data=csv,
                        file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data extracted. Try different fields or URLs.")
    
    elif main_tab == "🔬 Power Analysis":
        st.markdown("---")
        st.header("🔬 Power Analysis Mode")
        
        analysis_url = st.text_input("URL to Analyze", placeholder="https://example.com/products")
        
        if st.button("Analyze Structure", type="primary"):
            if not analysis_url or not validate_url(analysis_url):
                st.error("Invalid URL")
            else:
                with st.spinner("Fetching page..."):
                    html, engine_used, success = fetch_page_multi_engine(
                        analysis_url, engine, timeout, delay
                    )
                
                if not html or not success:
                    st.error("Failed to fetch page")
                else:
                    st.success(f"Page fetched using {engine_used}")
                    
                    # Analyze structure
                    analysis = analyze_page_structure(html)
                    
                    st.subheader("Structure Analysis")
                    st.json(analysis)
    
    # Footer
    st.markdown("---")
    st.caption("Built by Youssef Bassiony | AI Engineer ")


if __name__ == "__main__":
    main()
