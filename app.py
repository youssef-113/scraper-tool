import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import time
from io import BytesIO
import json

from scraper import (
    ScrapingEngine,
    fetch_page_multi_engine,
    analyze_structure_advanced,
    extract_data_robust,
    clean_data_advanced,
    PowerScraper,
    analyze_page_structure,
    smart_extract
)
from scraper.structure_ai import generate_fallback_selectors
from analysis import calculate_comprehensive_kpis, generate_comprehensive_insights
from utils import (
    validate_url,
    parse_fields,
    format_number,
    estimate_scraping_time,
    check_robots_txt,
    sanitize_filename,
    extract_domain
)

# Import RAG Analyzer components
from rag_analyzer import (
    DocumentProcessor,
    VectorStoreManager,
    ChatEngine,
    ProductExtractor
)

load_dotenv()

st.set_page_config(
    page_title="AI Web Scraper Pro + RAG Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    if 'scraping_results' not in st.session_state:
        st.session_state.scraping_results = None
    if 'kpis' not in st.session_state:
        st.session_state.kpis = None
    if 'insights' not in st.session_state:
        st.session_state.insights = None
    if 'structure_analysis' not in st.session_state:
        st.session_state.structure_analysis = None
    if 'power_analysis_data' not in st.session_state:
        st.session_state.power_analysis_data = None
    
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

def display_structure_analyzer(html: str, url: str):
    """Display advanced structure analysis"""
    st.subheader("🔬 Advanced Structure Analysis")
    
    with st.spinner("Analyzing page structure with PowerScraper..."):
        report = analyze_page_structure(html, url)
        st.session_state.structure_analysis = report
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏷️ Tags", "🎨 Classes", "📦 Containers", "🔗 Links", "🖼️ Images"
    ])
    
    with tab1:
        st.markdown("#### Most Common HTML Tags")
        tags_data = []
        for tag, count in report['most_common_tags']:
            tags_data.append({"Tag": tag, "Count": count})
        st.dataframe(pd.DataFrame(tags_data), use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("#### Most Common CSS Classes")
        classes_data = []
        for cls, count in report['most_common_classes'][:30]:
            classes_data.append({"Class": f".{cls}", "Count": count})
        st.dataframe(pd.DataFrame(classes_data), use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("#### Detected Data Containers")
        if report['repeating_patterns']:
            for idx, pattern in enumerate(report['repeating_patterns'][:10]):
                with st.expander(f"Pattern {idx+1}: {pattern['selector']} ({pattern['count']} occurrences)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Count", pattern['count'])
                    with col2:
                        st.metric("Avg Children", f"{pattern['avg_children']:.1f}")
                    with col3:
                        features = []
                        if pattern['has_text']:
                            features.append("📝 Text")
                        if pattern['has_links']:
                            features.append("🔗 Links")
                        if pattern['has_images']:
                            features.append("🖼️ Images")
                        st.write(" | ".join(features) if features else "No special features")
                    
                    st.code(pattern['sample_html'][:300], language='html')
        else:
            st.info("No repeating patterns detected.")
    
    with tab4:
        st.markdown("#### Link Elements")
        if report['link_elements']:
            links_df = pd.DataFrame(report['link_elements'][:20])
            st.dataframe(links_df[['selector', 'text', 'href']], use_container_width=True, hide_index=True)
    
    with tab5:
        st.markdown("#### Image Elements")
        if report['image_elements']:
            images_df = pd.DataFrame(report['image_elements'][:20])
            st.dataframe(images_df[['img_selector', 'alt', 'src']], use_container_width=True, hide_index=True)

def render_rag_analyzer_tab(api_key: str):
    """Render the RAG Data Analyzer tab"""
    st.header("📊 RAG Data Analyzer")
    st.markdown("**Upload CSV/Excel files and chat with your data using AI**")
    
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
            st.success(f"✅ File loaded: {uploaded_file.name}")
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
    
    if uploaded_file:
        try:
            # Load and process the file
            if st.session_state.uploaded_df is None or uploaded_file.name not in str(st.session_state.get('last_uploaded_file', '')):
                with st.spinner("Processing file..."):
                    df = st.session_state.doc_processor.load_file(uploaded_file)
                    st.session_state.uploaded_df = df
                    st.session_state.last_uploaded_file = uploaded_file.name
                    
                    # Create vector store if API key is available
                    if api_key:
                        # Analyze DataFrame
                        analysis = st.session_state.doc_processor.analyze_dataframe(df)
                        summary = st.session_state.doc_processor.generate_summary(df)
                        
                        # Create chunks and vector store
                        chunks = st.session_state.doc_processor.create_document_chunks(df, chunk_size=5)
                        
                        vector_store = VectorStoreManager(api_key)
                        vector_store.add_documents(chunks)
                        
                        st.session_state.vector_store = vector_store
                        st.session_state.chat_engine = ChatEngine(api_key, vector_store)
                        st.session_state.data_summary = summary
                        st.session_state.data_analysis = analysis
                    
                    st.success("✅ File processed successfully!")
            
            df = st.session_state.uploaded_df
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview",
                "💬 Chat with Data",
                "📦 Product Analysis",
                "📈 Statistics",
                "🔍 Data Explorer"
            ])
            
            with tab1:
                st.subheader("Dataset Overview")
                
                # Basic metrics
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("Total Rows", len(df))
                with metric_cols[1]:
                    st.metric("Total Columns", len(df.columns))
                with metric_cols[2]:
                    st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                with metric_cols[3]:
                    missing_pct = (df.isnull().sum().sum() / df.size * 100)
                    st.metric("Missing Data", f"{missing_pct:.1f}%")
                
                # Data summary
                st.markdown("#### Data Summary")
                if 'data_summary' in st.session_state:
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
                st.dataframe(df.head(10), use_container_width=True)
            
            with tab2:
                st.subheader("💬 Chat with Your Data")
                
                if not api_key:
                    st.warning("⚠️ Please enter your Groq API Key in the sidebar to use chat features")
                else:
                    # Chat interface
                    st.markdown("Ask questions about your data:")
                    
                    # Example questions
                    with st.expander("💡 Example Questions"):
                        st.markdown("""
                        - What is the average price of products?
                        - How many unique categories are there?
                        - What are the top 5 most expensive items?
                        - Show me products with rating above 4.5
                        - What is the price range for each category?
                        - Which brand has the most products?
                        - Summarize the key insights from this data
                        """)
                    
                    # Chat input
                    user_question = st.text_input(
                        "Ask a question:",
                        placeholder="e.g., What are the top 5 products by price?"
                    )
                    
                    col_ask, col_clear = st.columns([3, 1])
                    
                    with col_ask:
                        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
                    
                    with col_clear:
                        if st.button("🗑️ Clear History", use_container_width=True):
                            st.session_state.chat_history = []
                            if st.session_state.chat_engine:
                                st.session_state.chat_engine.clear_history()
                            st.rerun()
                    
                    if ask_button and user_question:
                        with st.spinner("Thinking..."):
                            answer = st.session_state.chat_engine.query(
                                user_question,
                                st.session_state.data_summary
                            )
                            
                            st.session_state.chat_history.append({
                                'question': user_question,
                                'answer': answer,
                                'timestamp': datetime.now().strftime("%H:%M:%S")
                            })
                    
                    # Display chat history
                    if st.session_state.chat_history:
                        st.markdown("---")
                        st.markdown("#### Conversation History")
                        
                        for i, chat in enumerate(reversed(st.session_state.chat_history)):
                            with st.container():
                                st.markdown(f"**🙋 Question ({chat['timestamp']}):** {chat['question']}")
                                st.markdown(f"**🤖 Answer:**")
                                st.markdown(chat['answer'])
                                st.markdown("---")
            
            with tab3:
                st.subheader("📦 Product Analysis")
                
                # Try to extract product-specific insights
                product_extractor = ProductExtractor(df)
                
                # Product summary
                st.markdown("#### Product Summary")
                product_summary = product_extractor.generate_product_summary()
                st.text(product_summary)
                
                # Price distribution
                price_stats = product_extractor.extract_price_stats()
                if price_stats:
                    st.markdown("#### Price Distribution")
                    price_col = st.columns(3)
                    with price_col[0]:
                        st.metric("Minimum", f"${price_stats['min_price']:.2f}")
                    with price_col[1]:
                        st.metric("Average", f"${price_stats['avg_price']:.2f}")
                    with price_col[2]:
                        st.metric("Maximum", f"${price_stats['max_price']:.2f}")
                
                # Category breakdown
                categories = product_extractor.extract_category_breakdown()
                if categories:
                    st.markdown("#### Category Breakdown")
                    cat_df = pd.DataFrame([
                        {'Category': cat, 'Count': count}
                        for cat, count in categories.items()
                    ])
                    st.dataframe(cat_df, use_container_width=True, hide_index=True)
                
                # Top products
                st.markdown("#### Top Products by Price")
                top_products = product_extractor.get_top_products(by='price', limit=10)
                st.dataframe(top_products, use_container_width=True)
            
            with tab4:
                st.subheader("📈 Statistical Analysis")
                
                # Numeric columns statistics
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.markdown("#### Numeric Columns Statistics")
                    st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
                # Categorical columns
                text_cols = df.select_dtypes(include=['object']).columns
                if len(text_cols) > 0:
                    st.markdown("#### Categorical Columns")
                    selected_cat = st.selectbox("Select column to analyze:", text_cols)
                    
                    if selected_cat:
                        value_counts = df[selected_cat].value_counts().head(20)
                        st.bar_chart(value_counts)
                        
                        st.markdown(f"**Top values in {selected_cat}:**")
                        st.dataframe(
                            pd.DataFrame({
                                'Value': value_counts.index,
                                'Count': value_counts.values
                            }),
                            use_container_width=True,
                            hide_index=True
                        )
                
                # Missing data analysis
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
                    st.success("✅ No missing data detected!")
            
            with tab5:
                st.subheader("🔍 Data Explorer")
                
                # Filtering options
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
                        unique_vals = df[filter_col].unique()
                        selected_vals = st.multiselect(
                            f"Select values for {filter_col}:",
                            unique_vals,
                            default=list(unique_vals[:5])
                        )
                        
                        if selected_vals:
                            filtered_df = df[df[filter_col].isin(selected_vals)]
                        else:
                            filtered_df = df
                    
                    st.markdown(f"**Filtered Results: {len(filtered_df)} rows**")
                    st.dataframe(filtered_df, use_container_width=True, height=400)
                    
                    # Download filtered data
                    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Filtered Data",
                        data=csv_data,
                        file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

def main():
    init_session_state()
    
    st.title("🤖 AI-Powered Universal Web Scraper PRO + RAG Data Analyzer")
    st.markdown("**Professional web scraping + Intelligent data analysis with AI**")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("🛠️ Scraping Engine")
        
        engine_options = {
            "AUTO (Recommended)": ScrapingEngine.AUTO,
            "Scrapling (Fast)": ScrapingEngine.SCRAPLING,
            "Playwright (JS Sites)": ScrapingEngine.PLAYWRIGHT,
            "Selenium (Compatible)": ScrapingEngine.SELENIUM,
            "Trafilatura (Content)": ScrapingEngine.TRAFILATURA
        }
        
        selected_engine = st.selectbox(
            "Select Engine",
            options=list(engine_options.keys()),
            index=0
        )
        
        engine = engine_options[selected_engine]
        
        st.markdown("---")
        st.subheader("🔬 Power Features")
        
        use_power_analysis = st.checkbox(
            "Enable Power Tag/Class Analysis",
            value=True,
            help="Advanced HTML structure analysis"
        )
        
        auto_detect_selectors = st.checkbox(
            "Auto-detect Best Selectors",
            value=True,
            help="Automatically find optimal CSS selectors"
        )
        
        st.markdown("---")
        st.subheader("⚡ Performance")
        
        timeout = st.slider(
            "Request Timeout (seconds)",
            min_value=10,
            max_value=120,
            value=30,
            step=5
        )
        
        delay = st.slider(
            "Delay Between Requests (seconds)",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.5
        )
        
        max_items = st.number_input(
            "Max Items Per URL",
            min_value=10,
            max_value=10000,
            value=500,
            step=50
        )
        
        st.markdown("---")
        st.subheader("🔒 Legal & Ethics")
        
        check_robots = st.checkbox(
            "Check robots.txt",
            value=True
        )
    
    # Main tabs
    main_tab = st.radio(
        "Select Feature:",
        ["🚀 Web Scraper", "🔬 Power Analysis", "📊 RAG Data Analyzer"],
        horizontal=True
    )
    
    if main_tab == "📊 RAG Data Analyzer":
        render_rag_analyzer_tab(api_key)
        return
    
    elif main_tab == "🔬 Power Analysis":
        st.markdown("---")
        st.header("🔬 Power Analysis Mode")
        
        analysis_url = st.text_input("URL to Analyze", placeholder="https://example.com/products")
        
        if st.button("🔍 Analyze Structure", type="primary"):
            if not analysis_url or not validate_url(analysis_url):
                st.error("Invalid URL")
                return
            
            with st.spinner("Fetching page..."):
                html, engine_used, success = fetch_page_multi_engine(analysis_url, engine, timeout, delay)
            
            if not html or not success:
                st.error("Failed to fetch page")
                return
            
            st.success(f"✅ Page fetched using {engine_used}")
            display_structure_analyzer(html, analysis_url)
        
        return
    
    # Web Scraper Mode
    st.markdown("---")
    
    if not api_key:
        st.warning("⚠️ Please enter your Groq API Key in the sidebar")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("📝 Input Configuration")
        
        urls_input = st.text_area(
            "Website URLs (one per line)",
            height=120,
            placeholder="https://example.com/products\nhttps://example.com/page2"
        )
        
        fields_input = st.text_input(
            "Data Fields (comma-separated)",
            placeholder="title, price, rating, description, image, brand"
        )
        
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        with col_ex1:
            if st.button("📦 E-commerce", use_container_width=True):
                st.session_state.example_fields = "title, price, rating, image, description"
        with col_ex2:
            if st.button("📰 News", use_container_width=True):
                st.session_state.example_fields = "title, author, date, content, category"
        with col_ex3:
            if st.button("🏠 Real Estate", use_container_width=True):
                st.session_state.example_fields = "title, price, bedrooms, bathrooms, location"
        
        if 'example_fields' in st.session_state:
            fields_input = st.session_state.example_fields
    
    with col2:
        st.subheader("📊 Quick Info")
        
        if urls_input and fields_input:
            urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
            fields = parse_fields(fields_input)
            
            st.metric("URLs to Scrape", len(urls))
            st.metric("Fields to Extract", len(fields))
            st.metric("Estimated Time", estimate_scraping_time(len(urls), delay))
    
    st.markdown("---")
    
    start_button = st.button(
        "🚀 Start Scraping",
        type="primary",
        use_container_width=True,
        disabled=not (urls_input and fields_input)
    )
    
    if start_button:
        if not urls_input or not fields_input:
            st.error("❌ Please provide both URLs and data fields")
            return
        
        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
        fields = parse_fields(fields_input)
        
        invalid_urls = [url for url in urls if not validate_url(url)]
        if invalid_urls:
            st.error(f"❌ Invalid URLs: {', '.join(invalid_urls)}")
            return
        
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            metrics_row = st.columns(4)
        
        all_data = []
        total_steps = len(urls) + 2
        current_step = 0
        start_time = time.time()
        
        for idx, url in enumerate(urls):
            current_step += 1
            progress = current_step / total_steps
            progress_bar.progress(progress)
            
            status_text.markdown(f"**🔍 Scraping {idx + 1}/{len(urls)}**: {url}")
            
            with metrics_row[0]:
                st.metric("Current", f"{idx + 1}/{len(urls)}")
            with metrics_row[1]:
                st.metric("Extracted", len(all_data))
            
            html, engine_used, success = fetch_page_multi_engine(
                url, engine, timeout, delay
            )
            
            if not html or not success:
                st.warning(f"⚠️ Failed to fetch: {url}")
                continue
            
            status_text.markdown(f"**🧠 Analyzing structure** ({engine_used})")
            
            selectors = None
            
            # Use Power Analysis if enabled
            if use_power_analysis and auto_detect_selectors:
                try:
                    scraper = PowerScraper(html, url)
                    best_container = scraper.find_best_container_selector()
                    
                    if best_container:
                        field_selectors = {}
                        for field in fields:
                            smart_sels = scraper.analyzer.generate_smart_selectors(field)
                            if smart_sels:
                                field_selectors[field] = {
                                    'primary_selector': smart_sels[0],
                                    'backup_selector': smart_sels[1] if len(smart_sels) > 1 else smart_sels[0],
                                    'attribute': 'text',
                                    'extraction_type': 'text'
                                }
                        
                        selectors = {
                            'container_selector': best_container,
                            'container_backup': best_container,
                            'fields': field_selectors
                        }
                        st.info(f"✨ Power Analysis: Using container '{best_container}'")
                except Exception as e:
                    st.warning(f"Power analysis failed, using AI: {str(e)}")
            
            # Fallback to AI analysis
            if not selectors and api_key:
                selectors = analyze_structure_advanced(html, fields, api_key, url)
            
            # Final fallback
            if not selectors:
                selectors = generate_fallback_selectors(fields)
            
            status_text.markdown(f"**📊 Extracting data**")
            
            data = extract_data_robust(html, selectors, fields, url, max_items)
            
            if data:
                all_data.extend(data)
                st.success(f"✅ Extracted {len(data)} items from {url}")
            else:
                st.warning(f"⚠️ No data from: {url}")
        
        if not all_data:
            st.error("❌ No data extracted")
            return
        
        current_step += 1
        progress_bar.progress(current_step / total_steps)
        status_text.markdown("**🧹 Cleaning data...**")
        
        df = clean_data_advanced(all_data, urls[0] if urls else '')
        
        if df.empty:
            st.error("❌ No valid data after cleaning")
            return
        
        current_step += 1
        progress_bar.progress(current_step / total_steps)
        
        kpis = calculate_comprehensive_kpis(df)
        
        insights = ""
        if api_key:
            insights = generate_comprehensive_insights(df, kpis, api_key, urls)
        
        progress_bar.progress(1.0)
        status_text.markdown("**✅ Complete!**")
        time.sleep(1)
        
        progress_bar.empty()
        status_text.empty()
        for col in metrics_row:
            col.empty()
        
        st.session_state.scraping_results = df
        st.session_state.kpis = kpis
        st.session_state.insights = insights
        
        total_time = int(time.time() - start_time)
        st.success(f"🎉 Scraped **{len(df)}** records from **{len(urls)}** URLs in **{total_time}s**!")
    
    # Display results
    if st.session_state.scraping_results is not None:
        df = st.session_state.scraping_results
        kpis = st.session_state.kpis
        insights = st.session_state.insights
        
        st.markdown("---")
        st.header("📊 Results Dashboard")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 KPIs", "🔍 Data", "🤖 Insights", "💾 Export"
        ])
        
        with tab1:
            st.subheader("Key Performance Indicators")
            
            kpi_cols = st.columns(5)
            with kpi_cols[0]:
                st.metric("📊 Records", kpis.get('total_records', 0))
            with kpi_cols[1]:
                st.metric("📋 Fields", kpis.get('total_fields', 0))
            with kpi_cols[2]:
                st.metric("✅ Quality", f"{kpis.get('quality_score', 0)}%")
            with kpi_cols[3]:
                st.metric("📊 Complete", f"{kpis.get('overall_completeness', 0)}%")
            with kpi_cols[4]:
                st.metric("🔄 Dupes", f"{kpis.get('duplicate_percentage', 0)}%")
        
        with tab2:
            st.subheader("Data Preview")
            st.dataframe(df, use_container_width=True, height=500)
        
        with tab3:
            st.subheader("🤖 AI Insights")
            st.markdown(insights)
        
        with tab4:
            st.subheader("💾 Export")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.csv"
            
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
