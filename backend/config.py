"""
Configuration settings for ReliableParts.com scraper
"""
import os
# URLs
BASE_URL = "https://www.reliableparts.com"
CATEGORIES = {
    "Refrigerator Parts": "/refrigerator-parts.html",
    "Dishwasher Parts": "/dishwasher-parts.html",
    "Washer Parts": "/washer-parts.html",
    "Dryer Parts": "/dryer-parts.html",
    # "Oven Range Parts": "/oven-range-parts.html"  # URL returns 404 - verify correct path
}

# Scraping Settings
DELAY_BETWEEN_REQUESTS = 2  # seconds
DELAY_BETWEEN_CATEGORIES = 5  # seconds
MAX_RETRIES = 3
TIMEOUT = 10  # seconds
SAVE_EVERY_N_PRODUCTS = 50

# Test Mode Settings
TEST_MODE_DELAY = 0.5  # seconds
TEST_MODE_LIMIT = 10  # products

# HTTP Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# CSS Selectors for Category Pages
CATEGORY_SELECTORS = {
    'product_grid': '.products.wrapper.grid.products-grid',
    'product_item': '.product-item',
    'product_link': '.product-item-link',
    'product_image': '.product-image-photo',
    'pagination': '.pages .item a.page',
    'next_page': '.pages .item.pages-item-next a',
}

# CSS Selectors for Product Pages
PRODUCT_SELECTORS = {
    'title': 'h1.page-title span, h1.page-title',
    'sku': '.product-sku, .product.attribute.sku .value, .sku .value',
    'price_regular': '.price-box .old-price .price, .old-price .price-wrapper .price',
    'price_sale': '.price-box .special-price .price, .special-price .price-wrapper .price',
    'price_current': '.product-info-price .price, .price-box .price, .price-wrapper .price',
    'stock_status': '.stock.available span, .stock span, .stock',
    'description': '.product.attribute.description .value, .product.description .value, .description .value',
    'overview': '.product.attribute.overview .value, .overview .value',
    'brand': '.product.attribute.brand .value, .brand .value',
    'images': '.product-image-photo, .fotorama__stage__frame img, .product-image-wrapper img, img.product-image-photo',
    'specifications': '.additional-attributes tbody tr, .product.attribute table tr',
    'compatible_models': '#tab-label-fits-models-title, .product.data.items, .fits-models',
}

# Output Settings
OUTPUT_DIR = "output"
CSV_FILENAME = "products.csv"
JSON_FILENAME = "products.json"
LOG_FILENAME = "scrape_log.txt"

# Data Fields
PRODUCT_FIELDS = [
    'sku',
    'product_name',
    'brand',
    'category',
    'subcategory',
    'product_url',
    'regular_price',
    'sale_price',
    'discount_percent',
    'subscribe_save_price',
    'in_stock',
    'stock_status',
    'description',
    'compatible_models',
    'specifications',
    'main_image_url',
    'all_image_urls',
    'scraped_at'
]

# Database Settings
DATABASE_PATH = "database/products.db"
CSV_INPUT_PATH = "output/products.csv"

# Data Validation Rules
REQUIRED_FIELDS = ["sku", "product_name"]
MAX_PRICE = 10000  # Sanity check for prices (dollars)
MIN_PRICE = 0

# OpenAI API Settings
OPENAI_API_KEY = os.getenv('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', '')
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.1  # Low for consistent outputs
OPENAI_MAX_TOKENS = 300

# Embedding Settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
EMBEDDING_BATCH_SIZE = 32

# Search Settings
DEFAULT_TOP_K = 5
ENABLE_UPSELLS = True
SIMILARITY_THRESHOLD = 0.3  # Minimum similarity score

# Response Settings
MAX_RESPONSE_LENGTH = 200  # words
INCLUDE_PRICING = True
INCLUDE_STOCK_STATUS = True
