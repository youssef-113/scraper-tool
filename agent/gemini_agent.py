"""
Gemini Live Agent - Core Implementation
Real-time, interruptible web scraping agent with multimodal capabilities
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional, Callable
import asyncio
import json
import os
from datetime import datetime
import base64


class GeminiScraperAgent:
    """Live conversational agent for web scraping using Gemini 2.0"""
    
    def __init__(self, api_key: str):
        """Initialize Gemini agent with live capabilities"""
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.0 Flash for multimodal + live
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        # Conversation state
        self.chat_session = None
        self.conversation_history: List[Dict[str, str]] = []
        self.scraping_context: Dict[str, Any] = {}
        self.is_active = False
        self.current_url: Optional[str] = None
        self.extracted_data: List[Dict] = []
        
    def start_session(self) -> bool:
        """Start chat session with Gemini"""
        try:
            self.chat_session = self.model.start_chat(
                enable_automatic_function_calling=True
            )
            self.is_active = True
            
            # Initialize with system context
            system_prompt = """You are an intelligent web scraping agent powered by Gemini.
            
Your capabilities:
1. Analyze webpage structures visually
2. Extract data based on natural language instructions
3. Answer questions about scraped data
4. Provide real-time progress updates
5. Accept interruptions and strategy changes

Be conversational, helpful, and efficient. Always confirm user instructions before scraping."""

            self.chat_session.send_message(system_prompt)
            return True
            
        except Exception as e:
            print(f"Error starting session: {e}")
            return False
    
    def process_voice_command(self, transcript: str) -> Dict[str, Any]:
        """Process voice command transcript into structured intent"""
        try:
            prompt = f"""Analyze this voice command and extract intent:
            
Command: "{transcript}"

Return JSON with:
{{
    "intent": "scrape|chat|modify|query|stop",
    "url": "extracted url or null",
    "fields": ["list of fields to extract"],
    "action": "specific action description",
    "confidence": 0.0-1.0
}}"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            return {
                'intent': 'unknown',
                'error': str(e),
                'original': transcript
            }
    
    def analyze_screenshot(self, image_data: bytes, question: str) -> Dict:
        """Analyze webpage screenshot with Gemini Vision"""
        try:
            # Multimodal prompt
            response = self.model.generate_content([
                {
                    'mime_type': 'image/png',
                    'data': image_data
                },
                f"""Analyze this webpage screenshot and answer: {question}
                
                Focus on:
                1. Visual structure and layout
                2. Data patterns and repeating elements
                3. Best CSS selectors for data extraction
                4. Recommendations for scraping strategy
                
                Return as JSON with keys: structure, patterns, selectors, strategy"""
            ])
            
            # Try to parse JSON response
            try:
                result = json.loads(response.text)
            except:
                result = {'analysis': response.text}
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def interactive_scraping(
        self, 
        url: str, 
        user_instructions: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """Interactive scraping with live feedback"""
        
        self.current_url = url
        self.update_context('url', url)
        self.update_context('instructions', user_instructions)
        
        # Build conversation
        conversation = f"""User wants to scrape: {url}

Instructions: {user_instructions}

I will help extract this data. Let me analyze the page structure first.

Steps:
1. Fetch the webpage
2. Analyze HTML structure
3. Identify data patterns
4. Extract requested fields
5. Provide results

Shall I proceed?"""

        if progress_callback:
            progress_callback("🤖 Analyzing target URL...")
        
        response = self.chat_session.send_message(conversation)
        
        return {
            'status': 'ready',
            'agent_response': response.text,
            'url': url,
            'session_id': datetime.now().isoformat()
        }
    
    def handle_interruption(self, user_input: str) -> str:
        """Handle user interruption during scraping"""
        try:
            prompt = f"""User interrupted with: "{user_input}"

Current scraping context:
{json.dumps(self.scraping_context, indent=2)}

Respond naturally and adjust the scraping strategy if needed.
Be conversational and helpful."""

            response = self.chat_session.send_message(prompt)
            
            # Store in history
            self.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            self.conversation_history.append({
                'role': 'assistant', 
                'content': response.text,
                'timestamp': datetime.now().isoformat()
            })
            
            return response.text
            
        except Exception as e:
            return f"Error handling interruption: {e}"
    
    def update_context(self, key: str, value: Any):
        """Update scraping context for agent awareness"""
        self.scraping_context[key] = value
        self.scraping_context['last_updated'] = datetime.now().isoformat()
    
    def generate_summary(self, scraped_data: List[Dict]) -> str:
        """Generate natural language summary of scraped data"""
        prompt = f"""Analyze this scraped data and provide a conversational summary:

Data (first 10 records):
{json.dumps(scraped_data[:10], indent=2)}

Total records: {len(scraped_data)}

Provide:
1. What was found (conversational tone)
2. Key insights and patterns
3. Data quality assessment
4. Suggestions for next steps

Be friendly and helpful!"""

        response = self.model.generate_content(prompt)
        return response.text
    
    def chat(self, message: str) -> str:
        """General chat with agent about scraping"""
        if not self.chat_session:
            self.start_session()
        
        # Add context awareness
        context = f"""Current scraping session context:
{json.dumps(self.scraping_context, indent=2)}

User message: {message}

Respond helpfully and naturally."""

        response = self.chat_session.send_message(context)
        
        # Store in history
        self.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': response.text,
            'timestamp': datetime.now().isoformat()
        })
        
        return response.text
    
    def suggest_selectors(self, html_sample: str, fields: List[str]) -> Dict:
        """Suggest CSS selectors for given fields"""
        prompt = f"""Analyze this HTML and suggest CSS selectors:

HTML Sample:
{html_sample[:5000]}

Target Fields: {', '.join(fields)}

Return JSON:
{{
    "container": "main container selector",
    "fields": {{
        "field_name": {{
            "selector": "CSS selector",
            "attribute": "text|href|src|data-*",
            "confidence": 0.0-1.0
        }}
    }}
}}"""

        response = self.model.generate_content(prompt)
        
        try:
            return json.loads(response.text)
        except:
            return {'raw_response': response.text}
    
    def close_session(self) -> str:
        """Close session gracefully"""
        if self.chat_session:
            try:
                farewell = self.chat_session.send_message(
                    "Session ending. Provide a friendly goodbye and brief summary."
                )
                self.is_active = False
                return farewell.text
            except:
                pass
        
        self.is_active = False
        return "Session closed. Thanks for using Gemini Scraper Agent!"
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation"""
        if not self.conversation_history:
            return "No conversation yet."
        
        summary = f"Conversation has {len(self.conversation_history)} messages.\n"
        summary += f"Current URL: {self.current_url or 'None'}\n"
        summary += f"Data extracted: {len(self.extracted_data)} records"
        
        return summary
