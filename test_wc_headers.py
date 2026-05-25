import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import config

url = f"{config.WC_URL.rstrip('/')}/wp-json/wc/v3/products/categories"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Testing direct requests.get to WooCommerce API with browser User-Agent...")
try:
    response = requests.get(
        url,
        auth=HTTPBasicAuth(config.WC_CONSUMER_KEY, config.WC_CONSUMER_SECRET),
        headers=headers,
        params={"search": "Electronics", "per_page": 20}
    )
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Failed requests.get test:", e)
