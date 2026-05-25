import os
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import config
from woocommerce import API

# Initialize API client using WP credentials
username = config.WP_USERNAME if config.WP_USERNAME else config.WC_CONSUMER_KEY
password = config.WP_APP_PASSWORD if config.WP_APP_PASSWORD else config.WC_CONSUMER_SECRET

wc = API(
    url=config.WC_URL,
    consumer_key=username,
    consumer_secret=password,
    version="wc/v3",
    timeout=30,
)

print("Testing wc.get('products/categories') with WP App Password client initialization...")
try:
    response = wc.get("products/categories", params={"search": "Electronics", "per_page": 20})
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Failed to GET categories:", e)
