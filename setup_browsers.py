import subprocess
import sys


def install_playwright():
    print("=" * 60)
    print("Installing Playwright browsers...")
    print("=" * 60)
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"], check=True
        )
        subprocess.run([sys.executable, "-m", "playwright", "install-deps"], check=True)
        print("Playwright installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Playwright installation failed: {e}")
        print("You can still use Scrapling and Selenium engines.")


def check_chromedriver():
    print("\n" + "=" * 60)
    print("Checking Selenium ChromeDriver...")
    print("=" * 60)
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("ChromeDriver working!")
    except Exception as e:
        print(f"ChromeDriver check failed: {e}")
        print("Please install ChromeDriver manually or use other engines.")


def main():
    print("\n" + "=" * 60)
    print("AI Web Scraper - Browser Setup")
    print("=" * 60 + "\n")

    install_playwright()
    check_chromedriver()

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nYou can now run: streamlit run app.py")


if __name__ == "__main__":
    main()
