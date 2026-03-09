import zipfile
import os

files_to_include = {
    # Root files
    "requirements.txt": "requirements.txt",
    ".env.example": ".env.example",
    "README.md": "README.md",
    "setup_browsers.py": "setup_browsers.py",
    "app.py": "app.py",

    # Scraper module
    "scraper/__init__.py": "scraper/__init__.py",
    "scraper/fetcher.py": "scraper/fetcher.py",
    "scraper/structure_ai.py": "scraper/structure_ai.py",
    "scraper/extractor.py": "scraper/extractor.py",
    "scraper/cleaner.py": "scraper/cleaner.py",
    "scraper/tag_class_analyzer.py": "scraper/tag_class_analyzer.py",

    # Analysis module
    "analysis/__init__.py": "analysis/__init__.py",
    "analysis/kpi.py": "analysis/kpi.py",
    "analysis/insights_ai.py": "analysis/insights_ai.py",

    # Utils module
    "utils/__init__.py": "utils/__init__.py",
    "utils/helpers.py": "utils/helpers.py"
}

zip_name = "ai_web_scraper_pro_v2.zip"

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for zip_path, file_path in files_to_include.items():
        if os.path.exists(file_path):
            zipf.write(file_path, f"ai_web_scraper/{zip_path}")
            print(f"✅ {zip_path}")
        else:
            print(f"⚠️ Missing: {file_path}")

print(f"\n✅ Created: {zip_name}")
print(f"📦 Size: {os.path.getsize(zip_name) / 1024:.1f} KB")
