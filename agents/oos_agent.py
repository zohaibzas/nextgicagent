"""
agents/oos_agent.py
Handles out-of-stock and back-in-stock updates.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools import vision, woocommerce as wc


def run(image_path: str, text_hint: str = "") -> dict:
    """
    Main entry point for OOS agent.
    Reads the screenshot, finds the product, updates stock status.
    Returns result summary.
    """
    print("\n[OOS Agent] Starting...")

    # Step 1: Extract product name, SKU, and action from screenshot
    print("  Reading screenshot...")
    data = vision.extract_oos_data(image_path)
    product_name = (data.get("product_name") or "").strip()
    sku          = (data.get("sku") or "").strip().lstrip("#").strip()
    action       = (data.get("action") or "outofstock").strip()

    # Allow text hint to override action.
    # Clients can type just 'OS' (out of stock) or 'Instock' as the WhatsApp caption.
    if text_hint:
        hint_lower = text_hint.strip().lower()
        if hint_lower in ("instock", "in stock", "back in stock") or \
           "instock" in hint_lower or "in stock" in hint_lower or "back in stock" in hint_lower:
            action = "instock"
        elif hint_lower in ("os", "oos", "out of stock", "out stock") or \
             "oos" in hint_lower or "out of stock" in hint_lower or "out stock" in hint_lower:
            action = "outofstock"

    print(f"  Product: '{product_name}' | SKU: '{sku}' | Action: {action}")

    if not sku and not product_name:
        return {"success": False, "error": "Could not extract product name or SKU from image"}

    # Step 2: Search WooCommerce
    product = None
    if sku:
        print(f"  Searching WooCommerce for SKU '{sku}'...")
        product = wc.search_product_by_sku(sku)

    if not product and product_name:
        print(f"  Searching WooCommerce for name '{product_name}'...")
        product = wc.search_product(product_name)

    if not product:
        identifier = f"SKU: {sku}" if sku else f"Name: {product_name}"
        if sku and product_name:
            identifier = f"SKU: {sku} or Name: {product_name}"
        return {
            "success": False,
            "error": f"Product not found: '{identifier}'",
            "product_name": product_name,
            "sku": sku,
            "action": action,
        }

    # Step 3: Update stock status
    result = wc.set_stock_status(product["id"], action)

    return {
        "success": True,
        "product_name": product["name"],
        "product_id": product["id"],
        "action": action,
        "message": f"'{product['name']}' marked as {action}",
    }
