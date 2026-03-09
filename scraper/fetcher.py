from typing import Optional, Tuple, Dict
from enum import Enum
import time
import random


class ScrapingEngine(Enum):
    SCRAPLING = "scrapling"
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    TRAFILATURA = "trafilatura"
    AUTO = "auto"


class WebFetcher:
    def __init__(self):
        try:
            from fake_useragent import UserAgent  # type: ignore

            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def get_random_headers(self) -> Dict[str, str]:
        user_agent = (
            self.ua.random
            if self.ua is not None
            else "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    def fetch_with_scrapling(self, url: str, timeout: int = 30) -> Optional[str]:
        try:
            from scrapling import Fetcher

            fetcher = Fetcher(auto_match=True, headless=True)
            page = fetcher.get(url, timeout=timeout)

            if page and page.html:
                return str(page.html)
            return None
        except Exception:
            return None

    def fetch_with_playwright(self, url: str, timeout: int = 30) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.get_random_headers()["User-Agent"],
                    viewport={"width": 1920, "height": 1080},
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
                time.sleep(2)
                html = page.content()
                browser.close()
                return html
        except Exception:
            return None

    def fetch_with_selenium(self, url: str, timeout: int = 30) -> Optional[str]:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument(
                f"user-agent={self.get_random_headers()['User-Agent']}"
            )
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            time.sleep(3)
            html = driver.page_source
            driver.quit()
            return html
        except Exception:
            return None

    def fetch_with_trafilatura(self, url: str, timeout: int = 30) -> Optional[str]:
        try:
            import trafilatura

            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return downloaded
            return None
        except Exception:
            return None


def fetch_page_multi_engine(
    url: str,
    engine: ScrapingEngine = ScrapingEngine.AUTO,
    timeout: int = 30,
    delay: float = 1.0,
    max_retries: int = 3,
) -> Tuple[Optional[str], str, bool]:
    fetcher = WebFetcher()

    if delay > 0:
        time.sleep(random.uniform(delay * 0.5, delay * 1.5))

    engines_to_try = []
    if engine == ScrapingEngine.AUTO:
        engines_to_try = [
            ScrapingEngine.SCRAPLING,
            ScrapingEngine.PLAYWRIGHT,
            ScrapingEngine.SELENIUM,
            ScrapingEngine.TRAFILATURA,
        ]
    else:
        engines_to_try = [engine]

    for attempt in range(max_retries):
        for eng in engines_to_try:
            try:
                html = None

                if eng == ScrapingEngine.SCRAPLING:
                    html = fetcher.fetch_with_scrapling(url, timeout)
                elif eng == ScrapingEngine.PLAYWRIGHT:
                    html = fetcher.fetch_with_playwright(url, timeout)
                elif eng == ScrapingEngine.SELENIUM:
                    html = fetcher.fetch_with_selenium(url, timeout)
                elif eng == ScrapingEngine.TRAFILATURA:
                    html = fetcher.fetch_with_trafilatura(url, timeout)

                if html and len(html) > 500:
                    return html, eng.value, True

            except Exception:
                continue

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    return None, "none", False


def fetch_multiple_pages(
    urls: list,
    engine: ScrapingEngine = ScrapingEngine.AUTO,
    timeout: int = 30,
    delay: float = 1.0,
) -> Dict[str, Dict]:
    results = {}

    for idx, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue

        html, engine_used, success = fetch_page_multi_engine(url, engine, timeout, delay)

        results[url] = {
            "html": html,
            "engine": engine_used,
            "success": success,
            "index": idx,
        }

    return results
