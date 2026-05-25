"""
agents/duplicate_agent.py
Handles product duplication with new SKUs and phone model attributes.
Attribute name is detected dynamically from the source product — not hardcoded.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tools import vision, woocommerce as wc


def detect_model_attribute(source_product: dict, target_model: str) -> str | None:
    """
    Look at the source product's attributes and find which one is most likely
    the 'phone model' attribute — i.e. the one whose value most closely matches
    the target model string (e.g. 'Galaxy S26 Ultra').

    Returns the attribute name, or None if nothing matches.
    """
    target_lower = target_model.lower()
    attributes   = source_product.get("attributes", [])

    if not attributes:
        return None

    # Score each attribute: does any of its current options resemble a phone model?
    phone_keywords = [
        "iphone", "samsung", "galaxy", "s2", "s3", "note", "pixel",
        "huawei", "xiaomi", "oneplus", "oppo", "vivo", "realme",
        "pro", "plus", "ultra", "max", "mini",
    ]

    best_attr = None
    best_score = 0

    for attr in attributes:
        options_text = " ".join(attr.get("options", [])).lower()
        score = sum(1 for kw in phone_keywords if kw in options_text)
        if score > best_score:
            best_score = score
            best_attr = attr["name"]

    if best_attr:
        print(f"  Auto-detected model attribute: '{best_attr}' (score: {best_score})")
    else:
        print("  No phone model attribute found — will skip attribute update")

    return best_attr


def run(image_path: str, text_hint: str = "") -> dict:
    """
    Main entry point for Duplicate agent.
    Reads duplication instructions, finds source product,
    creates N duplicates with new titles, SKUs, and attributes.
    """
    print("\n[Duplicate Agent] Starting...")

    # Step 1: Extract duplication data from screenshot
    print("  Reading screenshot...")
    data = vision.extract_duplicate_data(image_path)

    source_name = (data.get("source_product_name") or "").strip()
    duplicates  = data.get("duplicates") or []

    print(f"  Source product: '{source_name}'")
    print(f"  Duplicates to create: {len(duplicates)}")

    if not source_name:
        return {"success": False, "error": "Could not extract source product name"}

    if not duplicates:
        return {"success": False, "error": "No duplicate instructions found"}

    # Step 2: Find source product in WooCommerce
    print(f"  Searching WooCommerce for '{source_name}'...")
    source_product = wc.search_product(source_name)

    if not source_product:
        return {
            "success": False,
            "error": f"Source product not found: '{source_name}'",
        }

    source_id   = source_product["id"]
    source_name_actual = source_product["name"]
    print(f"  Found: '{source_name_actual}' (ID: {source_id})")

    # Fetch full product data (search results may omit attributes)
    full_source = wc.get_product_by_id(source_id)

    # Step 3: Auto-detect the phone model attribute from source product
    # Use the first duplicate's target_model as reference for detection
    first_model   = duplicates[0].get("target_model", "") if duplicates else ""
    attribute_name = detect_model_attribute(full_source, first_model)

    # Step 4: Create each duplicate
    results = []
    for dup in duplicates:
        target_model = dup.get("target_model", "")
        new_sku      = dup.get("sku", "")
        new_title    = dup.get("new_title", "")

        if not new_title:
            # Auto-generate: replace everything after last ' - ' with new model
            base = source_name_actual.rsplit(" - ", 1)[0].strip()
            new_title = f"{base} - {target_model}"

        print(f"\n  Creating: '{new_title}' | SKU: {new_sku} | Model: {target_model}")

        try:
            result = wc.duplicate_product(
                source_id=source_id,
                new_title=new_title,
                new_sku=new_sku,
                new_attribute_value=target_model,
                attribute_name=attribute_name,   # dynamically detected, not hardcoded
            )
            results.append({
                "success":    True,
                "title":      new_title,
                "sku":        new_sku,
                "product_id": result.get("id"),
                "target_model": target_model,
            })
        except Exception as e:
            results.append({
                "success": False,
                "title":   new_title,
                "sku":     new_sku,
                "error":   str(e),
            })

    success_count = sum(1 for r in results if r["success"])

    return {
        "success":        success_count > 0,
        "source_product": source_name_actual,
        "total":          len(duplicates),
        "created":        success_count,
        "failed":         len(duplicates) - success_count,
        "results":        results,
        "message":        f"Created {success_count}/{len(duplicates)} duplicates from '{source_name_actual}'",
    }
