from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Tag
import re
from urllib.parse import urljoin


def safe_extract_text(element: Optional[Tag]) -> str:
    if not element:
        return ""
    try:
        return element.get_text(strip=True)
    except Exception:
        return ""


def safe_extract_attribute(element: Optional[Tag], attr: str) -> str:
    if not element:
        return ""
    try:
        value = element.get(attr, "")
        return str(value) if value else ""
    except Exception:
        return ""


def extract_with_selector(container: Tag, selector_config: Dict, base_url: str = "") -> str:
    primary_selector = selector_config.get("primary_selector", "")
    backup_selector = selector_config.get("backup_selector", "")
    attribute = selector_config.get("attribute", "text")
    extraction_type = selector_config.get("extraction_type", "text")

    element = None

    if primary_selector:
        try:
            elements = container.select(primary_selector)
            if elements:
                element = elements[0]
        except Exception:
            pass

    if not element and backup_selector:
        try:
            elements = container.select(backup_selector)
            if elements:
                element = elements[0]
        except Exception:
            pass

    if not element:
        return ""

    value = ""

    if extraction_type == "text" or attribute == "text":
        value = safe_extract_text(element)
    elif extraction_type == "attribute":
        value = safe_extract_attribute(element, attribute)
        if value and attribute in ["href", "src"] and base_url:
            value = urljoin(base_url, value)
    elif extraction_type == "html":
        try:
            value = str(element)
        except Exception:
            value = safe_extract_text(element)

    return value


def extract_with_patterns(container: Tag, field: str) -> str:
    text_content = container.get_text(separator=" ", strip=True)
    field_lower = field.lower()

    if "price" in field_lower or "cost" in field_lower:
        price_patterns = [
            r"[$€£¥]\s*[\d,]+\.?\d*",
            r"[\d,]+\.?\d*\s*[$€£¥]",
            r"USD\s*[\d,]+\.?\d*",
            r"EUR\s*[\d,]+\.?\d*",
            r"Price:\s*[\d,]+\.?\d*",
        ]
        for pattern in price_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(0)

    elif "rating" in field_lower or "star" in field_lower:
        rating_patterns = [
            r"\d+\.?\d*\s*(?:out of|\/)\s*\d+",
            r"\d+\.?\d*\s*[★⭐]",
            r"Rating:\s*\d+\.?\d*",
        ]
        for pattern in rating_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(0)

    elif "email" in field_lower:
        email_match = re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text_content
        )
        if email_match:
            return email_match.group(0)

    elif "phone" in field_lower:
        phone_patterns = [
            r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
            r"\(\d{3}\)\s*\d{3}-\d{4}",
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text_content)
            if match:
                return match.group(0)

    elif "date" in field_lower:
        date_patterns = [
            r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
            r"\d{4}[/-]\d{1,2}[/-]\d{1,2}",
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(0)

    elif "url" in field_lower or "link" in field_lower:
        links = container.find_all("a", href=True)
        if links:
            return links[0].get("href", "")

    elif "image" in field_lower or "img" in field_lower:
        images = container.find_all("img", src=True)
        if images:
            return images[0].get("src", "")

    return ""


def extract_data_robust(
    html: str,
    selectors: Dict,
    fields: List[str],
    base_url: str = "",
    max_items: int = 1000,
) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")

    container_selector = selectors.get("container_selector", "")
    container_backup = selectors.get("container_backup", "")
    field_configs = selectors.get("fields", {})

    containers = []

    if container_selector:
        try:
            containers = soup.select(container_selector)
        except Exception:
            pass

    if not containers and container_backup:
        try:
            containers = soup.select(container_backup)
        except Exception:
            pass

    if not containers:
        potential_containers = soup.select("div, article, section, li, tr")
        containers = [c for c in potential_containers if len(list(c.children)) >= 2]

    if not containers:
        containers = [soup]

    containers = containers[:max_items]

    results = []

    for container in containers:
        item = {}
        has_data = False

        for field in fields:
            field = field.strip()
            value = ""

            if field in field_configs:
                value = extract_with_selector(container, field_configs[field], base_url)

            if not value:
                value = extract_with_patterns(container, field)

            if not value:
                field_lower = field.lower()
                field_keywords = [field, field_lower, field.replace("_", "-")]

                for keyword in field_keywords:
                    try:
                        elements = container.select(
                            f"[class*=\"{keyword}\"], [id*=\"{keyword}\"]"
                        )
                    except Exception:
                        elements = []
                    if elements:
                        value = safe_extract_text(elements[0])
                        if value:
                            break

            if value:
                has_data = True

            item[field] = value

        if has_data:
            item["_extraction_source"] = base_url
            results.append(item)

    return results
