from typing import Dict, List, Optional, Any, Tuple
from bs4 import BeautifulSoup, Tag
import re
from collections import Counter
from urllib.parse import urljoin


class TagClassAnalyzer:
    """Advanced analyzer for HTML tags, classes, and structure detection."""
    
    def __init__(self, html: str, base_url: str = ""):
        self.soup = BeautifulSoup(html, 'lxml')
        self.base_url = base_url
        self._tag_counts: Optional[Counter] = None
        self._class_counts: Optional[Counter] = None
        self._id_counts: Optional[Counter] = None
    
    def get_all_tags(self) -> Counter:
        """Count all HTML tags in the document."""
        if self._tag_counts is None:
            tags = [tag.name for tag in self.soup.find_all()]
            self._tag_counts = Counter(tags)
        return self._tag_counts
    
    def get_all_classes(self) -> Counter:
        """Count all CSS classes in the document."""
        if self._class_counts is None:
            classes = []
            for tag in self.soup.find_all():
                if tag.get('class'):
                    classes.extend(tag.get('class'))
            self._class_counts = Counter(classes)
        return self._class_counts
    
    def get_all_ids(self) -> Counter:
        """Count all IDs in the document."""
        if self._id_counts is None:
            ids = [tag.get('id') for tag in self.soup.find_all() if tag.get('id')]
            self._id_counts = Counter(ids)
        return self._id_counts
    
    def find_repeating_patterns(self, min_occurrences: int = 3) -> List[Dict]:
        """Find repeating element patterns that likely contain data."""
        patterns = []
        
        # Check for common container patterns
        candidates = [
            ('div', 'class'),
            ('article', 'class'),
            ('section', 'class'),
            ('li', 'class'),
            ('tr', 'class'),
            ('div', None),
        ]
        
        for tag, attr in candidates:
            if attr:
                elements = self.soup.find_all(tag, class_=True)
                class_groups: Dict[str, List[Tag]] = {}
                for elem in elements:
                    cls = ' '.join(sorted(elem.get('class', [])))
                    if cls:
                        class_groups.setdefault(cls, []).append(elem)
                
                for cls, elems in class_groups.items():
                    if len(elems) >= min_occurrences:
                        patterns.append(self._analyze_pattern(elems, f"{tag}.{cls.replace(' ', '.')}"))
            else:
                elements = self.soup.find_all(tag)
                if len(elements) >= min_occurrences:
                    # Group by similar structure
                    structure_groups: Dict[str, List[Tag]] = {}
                    for elem in elements:
                        struct_key = f"{len(list(elem.children))}_{self._get_element_signature(elem)}"
                        structure_groups.setdefault(struct_key, []).append(elem)
                    
                    for elems in structure_groups.values():
                        if len(elems) >= min_occurrences:
                            sample = elems[0]
                            cls = '.'.join(sample.get('class', [])) if sample.get('class') else 'item'
                            patterns.append(self._analyze_pattern(elems, f"{tag}.{cls}"))
        
        return sorted(patterns, key=lambda x: x['count'], reverse=True)
    
    def _analyze_pattern(self, elements: List[Tag], selector: str) -> Dict:
        """Analyze a repeating pattern."""
        sample = elements[0]
        children_count = [len(list(e.children)) for e in elements]
        
        has_text = any(e.get_text(strip=True) for e in elements)
        has_links = any(e.find_all('a', href=True) for e in elements)
        has_images = any(e.find_all('img', src=True) for e in elements)
        
        return {
            'selector': selector,
            'count': len(elements),
            'avg_children': sum(children_count) / len(children_count),
            'has_text': has_text,
            'has_links': has_links,
            'has_images': has_images,
            'sample_html': str(sample)[:500]
        }
    
    def _get_element_signature(self, elem: Tag) -> str:
        """Get a signature for element structure."""
        children = list(elem.children)
        if not children:
            return "empty"
        
        tag_names = [child.name for child in children if isinstance(child, Tag)]
        return '_'.join(tag_names[:5])  # First 5 child tags
    
    def find_links(self) -> List[Dict]:
        """Find all link elements."""
        links = []
        for a in self.soup.find_all('a', href=True):
            href = a.get('href', '')
            if href:
                links.append({
                    'selector': self._get_selector(a),
                    'text': a.get_text(strip=True)[:100],
                    'href': urljoin(self.base_url, href) if self.base_url else href,
                    'title': a.get('title', '')
                })
        return links
    
    def find_images(self) -> List[Dict]:
        """Find all image elements."""
        images = []
        for img in self.soup.find_all('img'):
            src = img.get('src', '')
            if src:
                images.append({
                    'img_selector': self._get_selector(img),
                    'src': urljoin(self.base_url, src) if self.base_url else src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        return images
    
    def _get_selector(self, element: Tag) -> str:
        """Generate a CSS selector for an element."""
        parts = []
        
        if element.get('id'):
            return f"#{element.get('id')}"
        
        if element.get('class'):
            classes = '.'.join(element.get('class'))
            parts.append(f"{element.name}.{classes}")
        else:
            parts.append(element.name)
        
        # Add nth-child if needed for specificity
        if element.parent:
            siblings = [s for s in element.parent.children if isinstance(s, Tag) and s.name == element.name]
            if len(siblings) > 1:
                idx = siblings.index(element) + 1
                parts[-1] += f":nth-child({idx})"
        
        return ' > '.join(parts[-2:]) if len(parts) > 1 else parts[0]
    
    def generate_smart_selectors(self, field_name: str) -> List[str]:
        """Generate smart CSS selectors for a field based on common patterns."""
        selectors = []
        field_lower = field_name.lower()
        
        # Common field patterns
        patterns = {
            'title': ['h1', 'h2', 'h3', '.title', '[class*="title"]', '[class*="heading"]', '[class*="name"]'],
            'price': ['.price', '[class*="price"]', '[data-price]', '.cost', '[class*="cost"]', 'span:contains("$")'],
            'image': ['img', '[class*="image"] img', '[class*="photo"] img', '[class*="thumb"] img'],
            'description': ['.description', '[class*="desc"]', '.summary', '[class*="content"]', 'p'],
            'rating': ['.rating', '[class*="rating"]', '[data-rating]', '.stars', '[class*="star"]'],
            'brand': ['.brand', '[class*="brand"]', '[class*="manufacturer"]', '.seller'],
            'availability': ['.stock', '[class*="stock"]', '[class*="availability"]', '.in-stock', '.out-of-stock'],
            'sku': ['.sku', '[class*="sku"]', '[data-sku]', '.product-code'],
            'category': ['.category', '[class*="category"]', '.breadcrumb', '[class*="breadcrumb"]'],
            'date': ['time', '[class*="date"]', '[class*="time"]', '[datetime]'],
            'author': ['.author', '[class*="author"]', '[class*="byline"]', '[rel="author"]'],
        }
        
        # Add specific patterns
        if field_lower in patterns:
            selectors.extend(patterns[field_lower])
        
        # Generic class-based selectors
        selectors.extend([
            f"[class*='{field_lower}']",
            f"[id*='{field_lower}']",
            f"[data-*='{field_lower}']",
        ])
        
        # Clean and validate selectors
        valid_selectors = []
        for sel in selectors:
            try:
                if self.soup.select(sel):
                    valid_selectors.append(sel)
            except Exception:
                continue
        
        return valid_selectors[:10]  # Return top 10
    
    def find_best_container(self) -> Optional[str]:
        """Find the best container selector for data items."""
        patterns = self.find_repeating_patterns(min_occurrences=3)
        
        if not patterns:
            return None
        
        # Score patterns by data richness
        best_score = 0
        best_selector = None
        
        for pattern in patterns[:5]:
            score = 0
            score += pattern['count'] * 2  # More occurrences = better
            score += pattern['avg_children']  # More children = more data
            if pattern['has_text']:
                score += 5
            if pattern['has_links']:
                score += 3
            if pattern['has_images']:
                score += 3
            
            if score > best_score:
                best_score = score
                best_selector = pattern['selector']
        
        return best_selector


class PowerScraper:
    """Enhanced scraper with smart analysis capabilities."""
    
    def __init__(self, html: str, base_url: str = ""):
        self.html = html
        self.base_url = base_url
        self.analyzer = TagClassAnalyzer(html, base_url)
        self.soup = BeautifulSoup(html, 'lxml')
    
    def find_best_container_selector(self) -> Optional[str]:
        """Find the best container for data extraction."""
        return self.analyzer.find_best_container()
    
    def extract_with_smart_selectors(self, fields: List[str]) -> List[Dict[str, Any]]:
        """Extract data using smart selector generation."""
        container_selector = self.find_best_container_selector()
        
        if not container_selector:
            container_selector = 'div, article, li, tr'  # Fallback
        
        containers = self.soup.select(container_selector)
        
        if not containers:
            containers = [self.soup]
        
        results = []
        
        for container in containers:
            item = {}
            has_data = False
            
            for field in fields:
                selectors = self.analyzer.generate_smart_selectors(field)
                value = self._extract_field(container, selectors)
                
                if value:
                    has_data = True
                item[field] = value
            
            if has_data:
                item['_container'] = container_selector
                results.append(item)
        
        return results
    
    def _extract_field(self, container: Tag, selectors: List[str]) -> str:
        """Try to extract a field using multiple selectors."""
        for selector in selectors:
            try:
                elements = container.select(selector)
                if elements:
                    # Try different extraction methods
                    elem = elements[0]
                    
                    # Text content
                    text = elem.get_text(strip=True)
                    if text:
                        return text
                    
                    # Common attributes
                    for attr in ['data-value', 'data-text', 'title', 'alt', 'content']:
                        val = elem.get(attr)
                        if val:
                            return str(val)
                    
                    # For images
                    if elem.name == 'img':
                        src = elem.get('src', '')
                        if src:
                            return urljoin(self.base_url, src)
                    
                    # For links
                    if elem.name == 'a':
                        href = elem.get('href', '')
                        if href:
                            return urljoin(self.base_url, href)
                            
            except Exception:
                continue
        
        return ''
    
    def get_structure_report(self) -> Dict[str, Any]:
        """Get a comprehensive structure analysis report."""
        return {
            'most_common_tags': self.analyzer.get_all_tags().most_common(20),
            'most_common_classes': self.analyzer.get_all_classes().most_common(50),
            'most_common_ids': self.analyzer.get_all_ids().most_common(20),
            'repeating_patterns': self.analyzer.find_repeating_patterns(min_occurrences=3),
            'link_elements': self.analyzer.find_links()[:50],
            'image_elements': self.analyzer.find_images()[:50],
            'total_elements': len(self.soup.find_all()),
        }


def analyze_page_structure(html: str, url: str = "") -> Dict[str, Any]:
    """Analyze page structure and return comprehensive report."""
    scraper = PowerScraper(html, url)
    return scraper.get_structure_report()


def smart_extract(html: str, fields: List[str], url: str = "") -> List[Dict[str, Any]]:
    """Extract data using smart analysis."""
    scraper = PowerScraper(html, url)
    return scraper.extract_with_smart_selectors(fields)
