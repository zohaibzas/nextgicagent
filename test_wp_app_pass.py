import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import config

url = f"{config.WC_URL.rstrip('/')}/wp-json/wc/v3/products/categories"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"Testing direct requests.get to WooCommerce API using WP_USERNAME and WP_APP_PASSWORD...")
print(f"Username: {config.WP_USERNAME}")
try:
    response = requests.get(
        url,
        auth=HTTPBasicAuth(config.WP_USERNAME, config.WP_APP_PASSWORD),
        headers=headers,
        params={"search": "Electronics", "per_page": 20}
    )
    print("Status code:", response.status_code)
    print("Response JSON:", response.json() if response.status_code == 200 else response.text[:500])
except Exception as e:
    print("Failed requests.get test:", e)
