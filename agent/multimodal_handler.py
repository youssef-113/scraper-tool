"""
Multimodal Handler - Vision + Voice Processing
Handles images, audio, and multimodal inputs for web scraping
"""

import base64
import io
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import os


class MultimodalHandler:
    """Handle multimodal inputs (vision, voice, screenshots)"""
    
    def __init__(self):
        self.supported_image_formats = ['png', 'jpg', 'jpeg', 'gif', 'webp']
        self.supported_audio_formats = ['wav', 'mp3', 'ogg', 'flac']
        self.max_image_size = 20 * 1024 * 1024  # 20MB
        self.max_audio_size = 10 * 1024 * 1024  # 10MB
    
    def encode_image(self, image_path: str) -> Optional[Tuple[bytes, str]]:
        """Encode image file to bytes with format detection"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Detect format
            ext = image_path.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg']:
                mime_type = 'image/jpeg'
            elif ext == 'png':
                mime_type = 'image/png'
            elif ext == 'gif':
                mime_type = 'image/gif'
            elif ext == 'webp':
                mime_type = 'image/webp'
            else:
                mime_type = 'image/png'  # Default
            
            return image_data, mime_type
            
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None
    
    def encode_image_from_pil(self, pil_image: Image.Image) -> Tuple[bytes, str]:
        """Convert PIL Image to bytes"""
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        image_data = buffer.getvalue()
        return image_data, 'image/png'
    
    def resize_image(
        self, 
        image_data: bytes, 
        max_width: int = 1920, 
        max_height: int = 1080
    ) -> bytes:
        """Resize image to fit within max dimensions"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Calculate resize ratio
            ratio = min(max_width / image.width, max_height / image.height)
            
            if ratio < 1:
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error resizing image: {e}")
            return image_data
    
    def capture_screenshot_data(self, screenshot_bytes: bytes) -> Dict[str, Any]:
        """Process screenshot data for analysis"""
        try:
            image = Image.open(io.BytesIO(screenshot_bytes))
            
            return {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'size_bytes': len(screenshot_bytes),
                'data': screenshot_bytes
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def extract_text_regions(self, image_data: bytes) -> list:
        """Extract text regions from image (placeholder for OCR)"""
        # This would integrate with vision models
        # For now, return placeholder
        return [
            {'region': 'header', 'text': 'Extracted text placeholder'},
            {'region': 'body', 'text': 'More extracted text'}
        ]
    
    def create_visual_prompt(
        self, 
        image_data: bytes, 
        question: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a multimodal prompt for vision analysis"""
        prompt = {
            'image': {
                'data': base64.b64encode(image_data).decode('utf-8'),
                'mime_type': 'image/png'
            },
            'question': question
        }
        
        if context:
            prompt['context'] = context
        
        return prompt
    
    def analyze_webpage_layout(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze webpage layout from screenshot"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Basic layout analysis
            width, height = image.size
            
            # Estimate layout regions
            header_region = (0, 0, width, int(height * 0.15))
            nav_region = (0, int(height * 0.15), int(width * 0.25), height)
            main_region = (int(width * 0.25), int(height * 0.15), width, height)
            
            return {
                'dimensions': {'width': width, 'height': height},
                'estimated_regions': {
                    'header': header_region,
                    'navigation': nav_region,
                    'main_content': main_region
                },
                'aspect_ratio': width / height,
                'is_responsive': width > 768
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_data_tables(self, image_data: bytes) -> list:
        """Detect potential data tables in screenshot"""
        # Placeholder for table detection
        # Would use vision models in production
        return [
            {
                'type': 'table',
                'confidence': 0.85,
                'estimated_rows': 10,
                'estimated_cols': 5
            }
        ]
    
    def detect_product_cards(self, image_data: bytes) -> list:
        """Detect product card patterns in screenshot"""
        # Placeholder for product card detection
        return [
            {
                'type': 'product_card',
                'confidence': 0.9,
                'estimated_count': 12
            }
        ]
    
    def encode_audio(self, audio_path: str) -> Optional[Tuple[bytes, str]]:
        """Encode audio file for processing"""
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            ext = audio_path.lower().split('.')[-1]
            mime_map = {
                'wav': 'audio/wav',
                'mp3': 'audio/mpeg',
                'ogg': 'audio/ogg',
                'flac': 'audio/flac'
            }
            
            mime_type = mime_map.get(ext, 'audio/wav')
            return audio_data, mime_type
            
        except Exception as e:
            print(f"Error encoding audio: {e}")
            return None
    
    def create_multimodal_context(
        self,
        text: Optional[str] = None,
        image_data: Optional[bytes] = None,
        audio_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Create combined multimodal context"""
        context = {}
        
        if text:
            context['text'] = text
        
        if image_data:
            context['image'] = {
                'data': base64.b64encode(image_data).decode('utf-8'),
                'mime_type': 'image/png'
            }
        
        if audio_data:
            context['audio'] = {
                'data': base64.b64encode(audio_data).decode('utf-8'),
                'mime_type': 'audio/wav'
            }
        
        return context
