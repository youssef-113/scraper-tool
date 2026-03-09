from scrapling.fetchers.playwright import PlaywrightFetcher

url = "https://www.eppendorf.com/us-en/Products-c-WebP-H-635425"

with PlaywrightFetcher(headless=True) as fetcher:
    response = fetcher.get(url)
    print(response.status)
    print(response.text[:500])