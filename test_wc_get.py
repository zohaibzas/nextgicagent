import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from tools.woocommerce import wc

print("Testing wc.get('products/categories')...")
try:
    response = wc.get("products/categories", params={"search": "Electronics", "per_page": 20})
    print("Status code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Failed to GET categories:", e)
