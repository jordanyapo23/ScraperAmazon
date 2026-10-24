from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AMAZON_DOMAIN = "www.amazon.fr"  # Change to www.amazon.com, www.amazon.ca, etc.
SEARCH_QUERY = "ASUS V16"
MAX_PAGES = 50
MAX_PRODUCTS = 10
PAGE_DELAY_SECONDS = 2.0
WAIT_SECONDS = 12
HEADLESS = False
KEEP_BROWSER_OPEN = True
DB_PATH = BASE_DIR / "data" / "products.sqlite3"
EXPORT_DIR = BASE_DIR / "exports"
