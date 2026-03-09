import re
from typing import List
from urllib.parse import urlparse
import requests
from urllib.robotparser import RobotFileParser


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except Exception:
        return False


def parse_fields(fields_input: str) -> List[str]:
    fields = [f.strip() for f in fields_input.split(",")]
    fields = [f for f in fields if f and not f.startswith("_")]
    return fields


def format_number(num: float) -> str:
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{num:.0f}"


def estimate_scraping_time(num_urls: int, delay: float) -> str:
    base_time_per_url = 5

    total_seconds = (num_urls * base_time_per_url) + (num_urls * delay)

    if total_seconds < 60:
        return f"~{int(total_seconds)} seconds"
    if total_seconds < 3600:
        minutes = int(total_seconds / 60)
        return f"~{minutes} minute{'s' if minutes > 1 else ''}"
    hours = int(total_seconds / 3600)
    return f"~{hours} hour{'s' if hours > 1 else ''}"


def check_robots_txt(url: str, user_agent: str = "*") -> tuple[bool, str]:
    try:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

        rp = RobotFileParser()
        rp.set_url(robots_url)

        try:
            rp.read()
        except Exception:
            return True, "No robots.txt found - scraping allowed"

        can_fetch = rp.can_fetch(user_agent, url)

        if can_fetch:
            return True, "Scraping allowed by robots.txt"
        return False, "Scraping disallowed by robots.txt"

    except Exception as e:
        return True, f"Could not check robots.txt: {str(e)}"


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r"[<>:\"/\\|?*]", "_", filename)
    return filename[:200]


def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return "unknown"
