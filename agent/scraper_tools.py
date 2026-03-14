"""
Scraper Tools - Web Scraping Functions
Integration with existing scraper module for Gemini agent
"""

from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime


class ScraperTools:
    """Web scraping tools for Gemini agent to use"""
    
    def __init__(self):
        self.last_result: Optional[Dict] = None
        self.scraping_history: List[Dict] = []
    
    def fetch_page(
        self, 
        url: str, 
        engine: str = "auto",
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Fetch webpage content"""
        try:
            # Import from existing scraper module
            from scraper import fetch_page_multi_engine, ScrapingEngine
            
            # Map engine string to enum
            engine_map = {
                'auto': ScrapingEngine.AUTO,
                'scrapling': ScrapingEngine.SCRAPLING,
                'playwright': ScrapingEngine.PLAYWRIGHT,
                'selenium': ScrapingEngine.SELENIUM,
                'trafilatura': ScrapingEngine.TRAFILATURA
            }
            
            selected_engine = engine_map.get(engine.lower(), ScrapingEngine.AUTO)
            
            # Fetch page
            html, engine_used, success = fetch_page_multi_engine(
                url=url,
                engine=selected_engine,
                timeout=timeout,
                delay=0.5
            )
            
            result = {
                'success': success,
                'url': url,
                'engine_used': engine_used,
                'html_length': len(html) if html else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            if success and html:
                result['html'] = html
                result['html_sample'] = html[:5000]  # Sample for analysis
            
            self.last_result = result
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def extract_data(
        self,
        html: str,
        fields: List[str],
        selectors: Optional[Dict] = None,
        max_items: int = 100
    ) -> Dict[str, Any]:
        """Extract data from HTML using selectors"""
        try:
            from scraper import extract_data_robust
            from scraper.structure_ai import generate_fallback_selectors
            
            # Use provided selectors or generate fallback
            if not selectors:
                selectors = generate_fallback_selectors(fields)
            
            # Extract data
            data = extract_data_robust(
                html=html,
                selectors=selectors,
                fields=fields,
                url=self.last_result.get('url', '') if self.last_result else '',
                max_items=max_items
            )
            
            result = {
                'success': bool(data),
                'records_extracted': len(data) if data else 0,
                'fields': fields,
                'data': data[:50] if data else [],  # Limit for response
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in history
            self.scraping_history.append(result)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'records_extracted': 0
            }
    
    def analyze_structure(
        self,
        html: str,
        target_fields: List[str]
    ) -> Dict[str, Any]:
        """Analyze HTML structure and suggest selectors"""
        try:
            from scraper import analyze_page_structure
            
            # Analyze page structure
            analysis = analyze_page_structure(html)
            
            result = {
                'success': True,
                'analysis': analysis,
                'target_fields': target_fields,
                'suggestions': self._generate_selector_suggestions(analysis, target_fields)
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_selector_suggestions(
        self,
        analysis: Dict,
        fields: List[str]
    ) -> Dict[str, str]:
        """Generate selector suggestions based on analysis"""
        suggestions = {}
        
        # Common patterns
        common_patterns = {
            'title': ['h1', '.title', '.product-title', '[itemprop="name"]'],
            'price': ['.price', '.product-price', '[itemprop="price"]', '.cost'],
            'description': ['.description', '.product-desc', '[itemprop="description"]', 'p'],
            'image': ['img', '.product-image', '[itemprop="image"]'],
            'rating': ['.rating', '.stars', '[itemprop="ratingValue"]'],
            'link': ['a', '.product-link', 'a[href]'],
            'brand': ['.brand', '.manufacturer', '[itemprop="brand"]'],
            'category': ['.category', '.product-category', '[itemprop="category"]']
        }
        
        for field in fields:
            field_lower = field.lower()
            if field_lower in common_patterns:
                suggestions[field] = common_patterns[field_lower]
            else:
                suggestions[field] = [f'.{field_lower}', f'#{field_lower}', f'[class*="{field_lower}"]']
        
        return suggestions
    
    def clean_data(
        self,
        data: List[Dict],
        remove_duplicates: bool = True
    ) -> Dict[str, Any]:
        """Clean and deduplicate scraped data"""
        try:
            from scraper import clean_data_advanced
            
            url = self.last_result.get('url', '') if self.last_result else ''
            
            # Clean data
            df = clean_data_advanced(data, url)
            
            result = {
                'success': True,
                'original_count': len(data),
                'cleaned_count': len(df),
                'duplicates_removed': len(data) - len(df) if remove_duplicates else 0,
                'columns': list(df.columns),
                'data': df.to_dict('records')[:50]
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_statistics(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for scraped data"""
        try:
            from analysis import calculate_comprehensive_kpis
            
            import pandas as pd
            df = pd.DataFrame(data)
            
            kpis = calculate_comprehensive_kpis(df)
            
            return {
                'success': True,
                'kpis': kpis,
                'total_records': len(data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for Gemini function calling"""
        return [
            {
                'name': 'fetch_page',
                'description': 'Fetch a webpage and return its HTML content',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'url': {
                            'type': 'string',
                            'description': 'The URL to fetch'
                        },
                        'engine': {
                            'type': 'string',
                            'enum': ['auto', 'scrapling', 'playwright', 'selenium', 'trafilatura'],
                            'description': 'The scraping engine to use'
                        }
                    },
                    'required': ['url']
                }
            },
            {
                'name': 'extract_data',
                'description': 'Extract structured data from HTML',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'fields': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'List of fields to extract'
                        },
                        'selectors': {
                            'type': 'object',
                            'description': 'CSS selectors for each field'
                        }
                    },
                    'required': ['fields']
                }
            },
            {
                'name': 'analyze_structure',
                'description': 'Analyze HTML structure to find data patterns',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'target_fields': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Fields to look for in the HTML'
                        }
                    },
                    'required': ['target_fields']
                }
            }
        ]
