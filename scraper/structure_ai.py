import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re


def extract_sample_content(html: str, max_chars: int = 20000) -> str:
    soup = BeautifulSoup(html, "lxml")

    for element in soup(["script", "style", "meta", "link", "noscript"]):
        element.decompose()

    body = soup.find("body")
    if body:
        text = str(body)
    else:
        text = str(soup)

    text = re.sub(r"\s+", " ", text)

    if len(text) > max_chars:
        return text[:max_chars]
    return text


def analyze_structure_advanced(
    html: str,
    fields: List[str],
    api_key: str,
    url: str = "",
) -> Optional[Dict]:
    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    except Exception:
        return None

    sample_html = extract_sample_content(html, max_chars=18000)

    prompt = f"""You are an expert web scraping engineer. Analyze this HTML and create robust selectors.

URL: {url}
Target Fields: {', '.join(fields)}

HTML Sample:
{sample_html}

TASK:
1. Identify repeating data containers (product cards, list items, table rows, articles, etc.)
2. Find the most specific and reliable CSS selector for the container
3. For each field, provide:
   - Primary CSS selector (relative to container)
   - Backup selector (alternative if primary fails)
   - Attribute to extract (text, href, src, data-*, etc.)

RETURN ONLY VALID JSON (no markdown, no explanations):

{{
  \"container_selector\": \"main CSS selector for repeating items\",
  \"container_backup\": \"backup container selector\",
  \"fields\": {{
    \"field_name\": {{
      \"primary_selector\": \"main CSS selector\",
      \"backup_selector\": \"alternative selector\",
      \"attribute\": \"text|href|src|data-price|etc\",
      \"extraction_type\": \"text|attribute|html\"
    }}
  }},
  \"pagination\": {{
    \"next_button\": \"selector for next page button\",
    \"page_links\": \"selector for page number links\"
  }},
  \"data_type\": \"product|article|listing|review|general\"
}}

Example:
{{
  \"container_selector\": \"div.product-card\",
  \"container_backup\": \"article.item\",
  \"fields\": {{
    \"title\": {{
      \"primary_selector\": \"h2.product-title\",
      \"backup_selector\": \"h3.title a\",
      \"attribute\": \"text\",
      \"extraction_type\": \"text\"
    }},
    \"price\": {{
      \"primary_selector\": \"span.price\",
      \"backup_selector\": \"div.pricing\",
      \"attribute\": \"data-price\",
      \"extraction_type\": \"attribute\"
    }},
    \"image\": {{
      \"primary_selector\": \"img.product-img\",
      \"backup_selector\": \"div.image img\",
      \"attribute\": \"src\",
      \"extraction_type\": \"attribute\"
    }}
  }},
  \"pagination\": {{
    \"next_button\": \"a.next-page\",
    \"page_links\": \"ul.pagination a\"
  }},
  \"data_type\": \"product\"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a web scraping expert. Return ONLY valid JSON without markdown formatting.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
        )

        content = response.choices[0].message.content.strip()

        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        content = content.strip()

        result = json.loads(content)

        required_keys = ["container_selector", "fields"]
        if not all(key in result for key in required_keys):
            return None

        return result

    except Exception:
        return None


def generate_fallback_selectors(fields: List[str]) -> Dict:
    common_selectors = {
        "title": {
            "primary_selector": "h1, h2, h3, .title, .product-title, .name",
            "backup_selector": "[class*=\"title\"], [class*=\"name\"], [class*=\"heading\"]",
            "attribute": "text",
            "extraction_type": "text",
        },
        "price": {
            "primary_selector": ".price, .cost, [class*=\"price\"], [data-price]",
            "backup_selector": "span:contains(\"$\"), span:contains(\"€\"), span:contains(\"£\")",
            "attribute": "text",
            "extraction_type": "text",
        },
        "image": {
            "primary_selector": "img",
            "backup_selector": "[style*=\"background-image\"]",
            "attribute": "src",
            "extraction_type": "attribute",
        },
        "description": {
            "primary_selector": ".description, .desc, p",
            "backup_selector": "[class*=\"desc\"], [class*=\"summary\"]",
            "attribute": "text",
            "extraction_type": "text",
        },
        "rating": {
            "primary_selector": ".rating, .stars, [class*=\"rating\"]",
            "backup_selector": "[data-rating], [class*=\"star\"]",
            "attribute": "text",
            "extraction_type": "text",
        },
        "link": {
            "primary_selector": "a",
            "backup_selector": "[href]",
            "attribute": "href",
            "extraction_type": "attribute",
        },
    }

    field_selectors = {}
    for field in fields:
        field_lower = field.lower()

        matched = False
        for key, selector_config in common_selectors.items():
            if key in field_lower:
                field_selectors[field] = selector_config
                matched = True
                break

        if not matched:
            field_selectors[field] = {
                "primary_selector": f"[class*=\"{field_lower}\"], [id*=\"{field_lower}\"]",
                "backup_selector": f"*:contains(\"{field}\")",
                "attribute": "text",
                "extraction_type": "text",
            }

    return {
        "container_selector": "div, article, li, tr, section",
        "container_backup": "*",
        "fields": field_selectors,
        "data_type": "general",
    }
