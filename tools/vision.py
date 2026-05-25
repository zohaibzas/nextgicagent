"""
tools/vision.py
Uses NVIDIA NIM API (Llama 3.2 90B Vision) to extract structured data from WhatsApp screenshots.
"""

import base64, json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from openai import OpenAI
import config

client = OpenAI(
    base_url=config.NVIDIA_BASE_URL,
    api_key=config.NVIDIA_API_KEY,
    timeout=60.0,
)

MODEL = config.NVIDIA_VISION_MODEL


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def ask_vision(image_path: str, prompt: str) -> str:
    """Send image + prompt to NVIDIA NIM Vision model, return text response."""
    b64 = encode_image(image_path)
    ext = image_path.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": prompt},
            ],
        }],
        max_tokens=1000,
    )
    content = response.choices[0].message.content
    if content is None:
        return ""
    return content.strip()


def clean_json_string(json_str: str) -> str:
    """Remove JS-style comments and trailing commas from a JSON string."""
    # Remove multi-line comments /* ... */
    json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)
    # Remove single-line comments // ... (not matching url schemes)
    json_str = re.sub(r"(?<!:)\/\/.*$", "", json_str, flags=re.MULTILINE)
    # Strip whitespace
    json_str = json_str.strip()
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    return json_str


def parse_fallback_markdown(text: str) -> dict:
    """
    If JSON parsing fails, try to parse markdown lists / bullet points.
    Matches lines like: * **Product Name:** Go-Des 4in1 Magnetic Holder
    """
    data = {}
    lines = text.split("\n")
    for line in lines:
        clean_line = line.strip().lstrip("*-#•").strip()
        if ":" not in clean_line:
            continue
        parts = clean_line.split(":", 1)
        key = parts[0].replace("**", "").replace("_", "").strip().lower()
        val = parts[1].replace("**", "").replace("_", "").strip()
        
        if "product name" in key or "source name" in key or "title" in key or "name" in key:
            if "image" not in key and "source" not in key:
                data["product_name"] = val
            elif "source" in key:
                data["source_product_name"] = val
        elif "price" in key:
            data["price"] = val
        elif "sku" in key:
            data["sku"] = val
        elif "category" in key or "location" in key:
            data["category_path"] = val
        elif "image" in key:
            data["has_product_image"] = "true" in val.lower() or "yes" in val.lower()
        elif "action" in key or "status" in key:
            data["action"] = val
            
    return data


def parse_json_response(text: str) -> dict:
    """Extract JSON from model response even if wrapped in markdown."""
    if not text or not text.strip():
        raise ValueError("Received empty or null response from the Vision model.")
    
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = clean_json_string(match.group())
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            fallback_data = parse_fallback_markdown(text)
            if fallback_data:
                return fallback_data
            raise ValueError(f"Failed to parse extracted JSON block from response. Error: {e}. Extracted JSON block:\n{json_str}")
            
    try:
        cleaned_text = clean_json_string(text)
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        fallback_data = parse_fallback_markdown(text)
        if fallback_data:
            return fallback_data
        raise ValueError(f"Failed to parse response as JSON. Error: {e}. Raw response:\n{text}")


# ── Task classifiers ──────────────────────────────────────────────────────────

def classify_task(image_path: str, text_message: str = "") -> dict:
    """
    Classify what task a WhatsApp message represents.
    Returns: { "task": "oos" | "duplicate" | "new_product" | "unknown", "confidence": 0-1 }
    """
    prompt = f"""
You are analyzing a WhatsApp message from an eCommerce client.
The client manages a WooCommerce store and sends product update requests.

Additional text in message: "{text_message}"

Classify this message into exactly ONE task:
1. "oos" — Client is reporting a product is OUT OF STOCK or back IN STOCK.
   Signals: text says "Instock", "OS", "OOS", "OUT STOCK", "out of stock", "back in stock",
   OR the image shows a handwritten "(OS)" or "(OJ)" or "OS" marking next to a product row.
2. "duplicate" — Client wants to DUPLICATE an existing product to new phone models with new SKUs
3. "new_product" — Client is submitting a completely NEW product with image, price, SKU, category

Respond ONLY with valid JSON, no explanation:
{{"task": "oos|duplicate|new_product|unknown", "confidence": 0.0-1.0, "reason": "brief reason"}}
"""
    response = ask_vision(image_path, prompt)
    return parse_json_response(response)


def extract_oos_data(image_path: str) -> dict:
    """
    Extract product name, SKU, and stock action from an OOS screenshot.
    Returns: { "product_name": str, "sku": str, "action": "outofstock" | "instock" }
    """
    prompt = """
This is a WhatsApp screenshot from an eCommerce client reporting stock status.
The image may show a product card, a message bubble, or a printed list/invoice of products.
A handwritten marking "(OS)", "(os)", "OS", or "os" next to or near a product indicates that the product is OUT OF STOCK.

Extract:
1. The product name: The exact product name as shown (e.g., "360 Rotation Case Black - iPad Mini 1/2/3/4/5").
2. The SKU: The product's SKU if visible (e.g. look for codes like "360RTN-IPDM123-BLK", which might be prefixed with "#" or enclosed in parentheses). If no SKU is visible, set it to null.
3. The action: Is the product "outofstock" OR "instock"?
   - If there is a handwritten "(OS)", "(os)", "OS", or "os" next to or near the product -> action is "outofstock"
   - If the product card shows an "OUT OF STOCK" badge -> action is "outofstock"
   - If the client says "Instock", "in stock", or "back in stock" -> action is "instock"
   - Default to "outofstock" if an OS marking or out-of-stock badge is present.

Respond ONLY with valid JSON:
{
  "product_name": "exact product name or null",
  "sku": "exact SKU string or null",
  "action": "outofstock or instock"
}
"""
    response = ask_vision(image_path, prompt)
    return parse_json_response(response)


def extract_duplicate_data(image_path: str) -> dict:
    """
    Extract duplication instructions from WhatsApp screenshot.
    Returns structured duplication task data.
    """
    prompt = """
This is a WhatsApp screenshot with product duplication instructions.
The client shows a source product and wants it duplicated for multiple phone models with new SKUs.

Extract ALL of the following:
1. source_product_name: The original product name (e.g. "Elegant Flower Magsafe Green – iPhone 17 Pro")
2. duplicates: A list of objects, one per new SKU/model, each with:
   - target_model: The phone model (e.g. "Samsung S26", "Samsung S26 Plus", "Samsung S26 Ultra")
   - sku: The new SKU for this duplicate
   - new_title: Suggested new product title (replace original phone model with target model)

Respond ONLY with valid JSON:
{
  "source_product_name": "...",
  "duplicates": [
    {"target_model": "...", "sku": "...", "new_title": "..."},
    ...
  ]
}
"""
    response = ask_vision(image_path, prompt)
    return parse_json_response(response)


def extract_new_product_data(image_path: str) -> dict:
    """
    Extract new product details from WhatsApp screenshot.
    Returns all fields needed to create the product.
    """
    prompt = """
This is a WhatsApp screenshot with a new product submission.
The message contains a product image and product details.

Extract ALL of the following fields:
1. product_name: Full product name
2. price: Price as a number (remove $ symbol)
3. sku: The SKU code
4. category_path: The location/category (e.g. "Accessories/gadgets/phone tag and cases")
5. has_product_image: true/false — does the message contain a product photo?

Respond ONLY with valid JSON:
{
  "product_name": "...",
  "price": "...",
  "sku": "...",
  "category_path": "...",
  "has_product_image": true
}
"""
    response = ask_vision(image_path, prompt)
    return parse_json_response(response)
