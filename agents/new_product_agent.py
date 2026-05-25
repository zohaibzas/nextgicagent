"""
agents/new_product_agent.py
Handles complete new product creation: image processing + WooCommerce upload.

Input cases this handles:
  Case A: Two separate messages — screenshot with text details + product image
  Case B: Single message — product image with text details typed in the message
  Case C: Single message — screenshot from website with embedded product image
"""

import sys, os, base64
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from openai import OpenAI
from tools import vision, woocommerce as wc, image_processor
import config

client = OpenAI(
    base_url=config.NVIDIA_BASE_URL,
    api_key=config.NVIDIA_API_KEY,
    timeout=60.0,
)


def _looks_like_screenshot(image_path: str) -> bool:
    """
    Ask Llama-3.2-Vision whether an image is a WhatsApp/website screenshot
    (containing UI chrome, text overlays, product cards)
    vs a clean product photo suitable for uploading.
    Returns True if it's a screenshot, False if it's a clean product photo.
    """
    b64 = base64.b64encode(open(image_path, "rb").read()).decode()
    ext = image_path.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"

    response = client.chat.completions.create(
        model=config.NVIDIA_VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": (
                    "Is this image a screenshot of a website or WhatsApp interface "
                    "(showing UI elements, text overlays, navigation bars, message bubbles, product cards)? "
                    "Or is it a clean product photo suitable for an eCommerce listing? "
                    "Reply with exactly one word: SCREENSHOT or PRODUCT"
                )},
            ],
        }],
        max_tokens=10,
    )
    answer = response.choices[0].message.content.strip().upper()
    print(f"  Image type check '{os.path.basename(image_path)}': {answer}")
    return answer == "SCREENSHOT"


def _separate_images(image_paths: list[str]) -> tuple[str | None, str | None]:
    """
    Given a list of image paths, identify which is the details screenshot
    and which is the clean product photo.

    Returns: (screenshot_path, product_image_path)
    Either can be None if not found.
    """
    if not image_paths:
        return None, None

    if len(image_paths) == 1:
        path = image_paths[0]
        if _looks_like_screenshot(path):
            return path, None   # only screenshot, no product image
        else:
            return None, path   # only product image, no text screenshot

    # Multiple images: classify each
    screenshots = []
    products    = []
    for p in image_paths:
        if _looks_like_screenshot(p):
            screenshots.append(p)
        else:
            products.append(p)

    screenshot    = screenshots[0] if screenshots else None
    product_image = products[0]    if products    else None
    return screenshot, product_image


def _extract_details_from_text(text: str) -> dict:
    """
    Extract product details from raw text message using LLM.
    """
    if not text or not text.strip():
        return {}

    prompt = f"""
You are an expert data extraction assistant.
Extract product details from this WhatsApp text message:
---
{text}
---

Extract the following fields ONLY if they are explicitly mentioned in the text:
1. "product_name": Full product name/title. Look for lines like "Title: ...", "Name: ...", or a title listed under the header. Extract the complete string exactly as written on that line (including any trailing model numbers, colors, parentheses, etc.), without modifying, shortening, or truncating it.
2. "price": The product price. Strip any currency symbols (e.g. if "$20", return "20").
3. "sku": The SKU code (e.g. "AM9PRO-CRM").
4. "category_path": The category or location path (e.g. "Accessories/Headphones/Wireless Headsets").

Respond ONLY with valid JSON. Do not include any markdown formatting, code blocks, or extra text.
If a field is not explicitly present in the text, set it to null.

JSON structure:
{{
  "product_name": null,
  "price": null,
  "sku": null,
  "category_path": null
}}
"""
    try:
        response = client.chat.completions.create(
            model=config.NVIDIA_VISION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()
        from tools import vision
        data = vision.parse_json_response(content)
        return {k: v for k, v in data.items() if v is not None and str(v).strip() != ""}
    except Exception as e:
        print(f"  Error extracting details from text message: {e}")
        return {}


def run(image_paths: list[str], text_hint: str = "") -> dict:
    """
    Main entry point for New Product agent.

    Args:
        image_paths: All images from the WhatsApp message(s)
        text_hint:   Any text typed alongside the images
    """
    print("\n[New Product Agent] Starting...")

    if not image_paths:
        return {"success": False, "error": "No images provided"}

    # Step 1: Extract details from text_hint first (highest priority)
    text_data = {}
    if text_hint:
        print("  Extracting product details from text hint...")
        text_data = _extract_details_from_text(text_hint)
        print(f"  Details from text: {text_data}")

    # Step 2: Classify which image is the details screenshot vs product photo
    print(f"  Classifying {len(image_paths)} image(s)...")
    screenshot_path, product_image_path = _separate_images(image_paths)

    print(f"  Screenshot:    {os.path.basename(screenshot_path) if screenshot_path else 'None'}")
    print(f"  Product image: {os.path.basename(product_image_path) if product_image_path else 'None'}")

    # Step 3: Extract product details from image if needed
    image_data = {}
    details_source = screenshot_path or product_image_path
    if details_source:
        print(f"  Extracting product details from image: {os.path.basename(details_source)}")
        image_data = vision.extract_new_product_data(details_source)
        print(f"  Details from image: {image_data}")

    # Step 4: Merge: text_data has priority over image_data
    data = {}
    for key in ["product_name", "price", "sku", "category_path"]:
        val = text_data.get(key)
        if val is None or str(val).strip() == "":
            val = image_data.get(key)
        data[key] = val

    # Fallback to regex-based extraction if fields are still missing
    if text_hint:
        data = _merge_text_hint(data, text_hint)

    product_name  = (data.get("product_name") or "").strip()
    price_val     = data.get("price")
    price         = str(price_val).replace("$", "").strip() if price_val is not None else "0"
    sku           = (data.get("sku") or "").strip()
    category_path = (data.get("category_path") or "").strip()

    print(f"  Final Name:     {product_name}")
    print(f"  Final Price:    ${price}")
    print(f"  Final SKU:      {sku}")
    print(f"  Final Category: {category_path}")

    # Validate required fields
    missing = []
    if not product_name: missing.append("product_name")
    if not sku:          missing.append("SKU")
    if not price or price == "0": missing.append("price")
    if missing:
        return {
            "success": False,
            "error": f"Missing required fields: {', '.join(missing)}. "
                     f"Please ensure the message includes product name, SKU, and price.",
        }

    # Step 5: Determine which image to process for the product listing
    image_to_process = product_image_path or screenshot_path

    if not image_to_process:
        return {"success": False, "error": "No usable product image found"}

    print(f"  Processing image: {os.path.basename(image_to_process)}")
    processed_image = image_processor.process_product_image(image_to_process)

    # Step 6: Create product in WooCommerce
    print("  Creating product in WooCommerce...")
    result = wc.create_product(
        title=product_name,
        sku=sku,
        price=price,
        category_path=category_path,
        image_path=processed_image,
    )

    # Clean up processed image
    try:
        os.remove(processed_image)
    except Exception:
        pass

    if "id" in result:
        return {
            "success":      True,
            "product_name": product_name,
            "product_id":   result["id"],
            "sku":          sku,
            "price":        price,
            "permalink":    result.get("permalink", ""),
            "message":      f"'{product_name}' created (ID: {result['id']}, SKU: {sku})",
        }
    else:
        return {
            "success":      False,
            "error":        f"WooCommerce error: {result}",
            "product_name": product_name,
        }


def _merge_text_hint(data: dict, text: str) -> dict:
    """
    If GPT missed any fields, try to pull them from the raw text message.
    Simple keyword extraction — not exhaustive, just a safety net.
    """
    import re

    text_lower = text.lower()

    if not data.get("product_name"):
        title_match = re.search(r"title[:\s]+(.+)", text, re.IGNORECASE)
        if title_match:
            data["product_name"] = title_match.group(1).strip()
            print(f"  Title from text hint: {data['product_name']}")

    if not data.get("sku"):
        sku_match = re.search(r"\bsku[:\s]+([A-Z0-9\-]+)", text, re.IGNORECASE)
        if sku_match:
            data["sku"] = sku_match.group(1).strip()
            print(f"  SKU from text hint: {data['sku']}")

    if not data.get("price") or data.get("price") == "0":
        price_match = re.search(r"\$\s?(\d+(?:\.\d{1,2})?)", text)
        if price_match:
            data["price"] = price_match.group(1)
            print(f"  Price from text hint: ${data['price']}")

    if not data.get("category_path"):
        loc_match = re.search(r"location[:\s]+(.+)", text, re.IGNORECASE)
        if loc_match:
            data["category_path"] = loc_match.group(1).strip()
            print(f"  Category from text hint: {data['category_path']}")

    return data
