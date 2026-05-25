"""
tools/woocommerce.py
All WooCommerce REST API operations used by agents.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from woocommerce import API
from rapidfuzz import fuzz, process
import config

# Initialize WooCommerce REST API client.
# Prefer WordPress Application Password credentials if configured, as WooCommerce API keys may expire/fail.
username = config.WP_USERNAME if config.WP_USERNAME else config.WC_CONSUMER_KEY
password = config.WP_APP_PASSWORD if config.WP_APP_PASSWORD else config.WC_CONSUMER_SECRET

wc = API(
    url=config.WC_URL,
    consumer_key=username,
    consumer_secret=password,
    version="wc/v3",
    timeout=30,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
)


# ── Search ────────────────────────────────────────────────────────────────────

def search_product_by_sku(sku: str) -> dict | None:
    """
    Search WooCommerce for a product by exact SKU.
    Returns the product dict, or None.
    """
    if not sku:
        return None
    response = wc.get("products", params={"sku": sku})
    if response.status_code != 200:
        print(f"  WooCommerce API Error (search_product_by_sku): {response.status_code} - {response.text}")
        return None

    results = response.json()
    if isinstance(results, list) and results:
        print(f"  Matched exact SKU: '{sku}' -> '{results[0].get('name')}'")
        return results[0]

    print(f"  No SKU match for '{sku}'")
    return None


def search_product(name: str) -> dict | None:
    """
    Search WooCommerce for a product by name.
    Uses fuzzy matching to handle slight name variations.
    Returns the best matching product dict, or None.
    """
    # Direct search via API first
    response = wc.get("products", params={"search": name, "per_page": 10})
    if response.status_code != 200:
        print(f"  WooCommerce API Error (search_product): {response.status_code} - {response.text}")
        return None

    results = response.json()
    if not isinstance(results, list):
        print(f"  Unexpected response format for search: {results}")
        return None

    if not results:
        return None

    # Fuzzy match against returned names
    names = [p.get("name", "") for p in results if isinstance(p, dict)]
    if not names:
        return None

    match = process.extractOne(name, names, scorer=fuzz.token_sort_ratio)

    if match and match[1] >= config.FUZZY_MATCH_THRESHOLD:
        idx = names.index(match[0])
        print(f"  Matched: '{name}' -> '{match[0]}' ({match[1]}% confidence)")
        return results[idx]

    print(f"  No confident match for '{name}' (best: {match})")
    return None


def get_product_by_id(product_id: int) -> dict:
    """Fetch full product data by ID."""
    response = wc.get(f"products/{product_id}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch product by ID {product_id}: {response.status_code} {response.text}")
    return response.json()


# ── Stock Management ──────────────────────────────────────────────────────────

def set_stock_status(product_id: int, status: str) -> dict:
    """
    Set product stock status.
    status: 'instock' | 'outofstock' | 'onbackorder'
    """
    payload = {
        "stock_status": status,
        "manage_stock": False,
    }
    response = wc.put(f"products/{product_id}", data=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to set stock status for product ID {product_id}: {response.status_code} {response.text}")
    result = response.json()
    print(f"  Stock updated -> ID {product_id}: {status}")
    return result


# ── Duplication ───────────────────────────────────────────────────────────────

def duplicate_product(source_id: int, new_title: str, new_sku: str,
                      new_attribute_value: str = None,
                      attribute_name: str = None) -> dict:
    """
    Duplicate a WooCommerce product with a new title, SKU, and optional attribute.
    Returns the newly created product dict.
    """
    source = get_product_by_id(source_id)

    # Fields to strip (WooCommerce rejects these on POST)
    strip = {"id", "date_created", "date_modified", "date_created_gmt",
             "date_modified_gmt", "permalink", "status"}

    payload = {k: v for k, v in source.items() if k not in strip}

    # Apply changes
    payload["name"]   = new_title
    payload["sku"]    = new_sku
    payload["slug"]   = ""   # WooCommerce auto-generates from title
    payload["status"] = "publish"

    # Update specific attribute value if provided
    if new_attribute_value and attribute_name:
        for attr in payload.get("attributes", []):
            if attr["name"].lower() == attribute_name.lower():
                attr["options"] = [new_attribute_value]

    response = wc.post("products", data=payload)
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to duplicate product: {response.status_code} {response.text}")
    result = response.json()

    if "id" in result:
        print(f"  Duplicated → '{new_title}' (ID: {result['id']}, SKU: {new_sku})")
    else:
        print(f"  Duplication failed: {result}")

    return result


# ── Product Creation ──────────────────────────────────────────────────────────

def get_or_create_category(category_path: str) -> list[int]:
    """
    Takes a category path like 'Accessories/gadgets/phone tag and cases'
    Creates missing categories and returns list of category IDs.
    """
    parts = [p.strip() for p in category_path.split("/")]
    category_ids = []
    parent_id = 0

    for part in parts:
        # Search for existing category
        response = wc.get("products/categories", params={
            "search": part, "per_page": 20
        })
        if response.status_code != 200:
            raise Exception(f"Failed to fetch categories: {response.status_code} {response.text}")
        existing = response.json()
        if not isinstance(existing, list):
            raise Exception(f"Unexpected response format for categories: {existing}")

        match = next((c for c in existing
                      if isinstance(c, dict)
                      and c.get("name", "").lower() == part.lower()
                      and c.get("parent") == parent_id), None)

        if match:
            cat_id = match["id"]
        else:
            # Create new category under parent
            new_cat_response = wc.post("products/categories", data={
                "name": part,
                "parent": parent_id,
            })
            if new_cat_response.status_code not in (200, 201):
                raise Exception(f"Failed to create category '{part}': {new_cat_response.status_code} {new_cat_response.text}")
            new_cat = new_cat_response.json()
            cat_id = new_cat["id"]
            print(f"  Created category: '{part}' (ID: {cat_id})")

        category_ids.append(cat_id)
        parent_id = cat_id

    return category_ids


def upload_image(image_path: str) -> tuple[int, str]:
    """
    Upload an image to WordPress media library.
    Returns a tuple of (attachment ID, source URL).
    """
    import requests
    from requests.auth import HTTPBasicAuth

    filename = os.path.basename(image_path)
    media_url = f"{config.WC_URL.rstrip('/')}/wp-json/wp/v2/media"

    # Use WordPress credentials if provided, fallback to WooCommerce credentials
    username = config.WP_USERNAME if config.WP_USERNAME else config.WC_CONSUMER_KEY
    password = config.WP_APP_PASSWORD if config.WP_APP_PASSWORD else config.WC_CONSUMER_SECRET

    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "image/jpeg",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    with open(image_path, "rb") as f:
        response = requests.post(
            media_url,
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            data=f.read(),
            timeout=30,
        )

    if response.status_code == 201:
        media_id = response.json()["id"]
        media_url_src = response.json()["source_url"]
        print(f"  Image uploaded: {filename} (ID: {media_id})")
        return media_id, media_url_src
    else:
        raise Exception(f"Image upload failed: {response.status_code} {response.text}")


def create_product(title: str, sku: str, price: str,
                   category_path: str, image_path: str,
                   tags: list[str] = None, description: str = "") -> dict:
    """
    Create a brand new WooCommerce product.
    """
    # Upload image
    media_id, media_url_src = upload_image(image_path)

    # Resolve categories
    category_ids = get_or_create_category(category_path)

    # Resolve tags
    tag_ids = []
    if tags:
        for tag in tags:
            response = wc.get("products/tags", params={"search": tag})
            if response.status_code != 200:
                print(f"  Failed to fetch tags for '{tag}': {response.status_code} {response.text}")
                continue
            existing = response.json()
            if not isinstance(existing, list):
                print(f"  Unexpected response format for tags: {existing}")
                continue

            match = next((t for t in existing
                          if isinstance(t, dict)
                          and t.get("name", "").lower() == tag.lower()), None)
            if match:
                tag_ids.append({"id": match["id"]})
            else:
                new_tag_response = wc.post("products/tags", data={"name": tag})
                if new_tag_response.status_code not in (200, 201):
                    print(f"  Failed to create tag '{tag}': {new_tag_response.status_code} {new_tag_response.text}")
                    continue
                new_tag = new_tag_response.json()
                tag_ids.append({"id": new_tag["id"]})

    payload = {
        "name":              title,
        "sku":               sku,
        "regular_price":     str(price),
        "description":       description,
        "status":            "publish",
        "catalog_visibility":"visible",
        "images":            [{"id": media_id, "src": media_url_src, "position": 0}],
        "categories":        [{"id": cid} for cid in category_ids],
        "tags":              tag_ids,
    }

    response = wc.post("products", data=payload)
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to create product in WooCommerce: {response.status_code} {response.text}")
    result = response.json()

    if "id" in result:
        print(f"  Product created: '{title}' (ID: {result['id']})")
    else:
        print(f"  Product creation failed: {result}")

    return result
