"""
tools/image_processor.py
Processes product images using the PSD template zone.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PIL import Image
from psd_tools import PSDImage
import config

# ── Load zone from PSD once at import ────────────────────────────────────────
DEFAULT_ZONE = (206, 74, 593, 719)

def _load_zone() -> tuple:
    try:
        psd = PSDImage.open(config.PSD_TEMPLATE_PATH)
        for layer in psd:
            if layer.kind == "smartobject":
                x1, y1, x2, y2 = layer.bbox
                print(f"  PSD zone loaded: ({x1},{y1}) -> ({x2},{y2})")
                return (x1, y1, x2, y2)
    except Exception as e:
        print(f"  PSD load warning: {e} - using default zone")
    return DEFAULT_ZONE

ZONE = _load_zone()

CANVAS_SIZE  = (800, 800)
BG_COLOR     = (255, 255, 255)
JPEG_QUALITY = 95
DPI          = 72


def process_product_image(input_path: str, output_path: str = None) -> str:
    """
    Place product image into PSD template zone, export as JPEG.
    Returns the output path.
    """
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)

    if output_path is None:
        basename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(config.PROCESSED_DIR, f"{basename}_processed.jpg")

    x1, y1, x2, y2 = ZONE
    zone_w = x2 - x1
    zone_h = y2 - y1

    product = Image.open(input_path).convert("RGBA")
    product.thumbnail((zone_w, zone_h), Image.LANCZOS)

    offset_x = x1 + (zone_w - product.width) // 2
    offset_y = y1 + (zone_h - product.height) // 2

    canvas = Image.new("RGB", CANVAS_SIZE, BG_COLOR)
    canvas.paste(product, (offset_x, offset_y), product)
    canvas.save(output_path, "JPEG", quality=JPEG_QUALITY, dpi=(DPI, DPI))

    print(f"  Image processed: {output_path}")
    return output_path


def process_folder(folder_path: str, output_folder: str = None) -> list[str]:
    """Process all images in a folder. Returns list of output paths."""
    if output_folder is None:
        output_folder = os.path.join(folder_path, "processed")

    os.makedirs(output_folder, exist_ok=True)
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    files = [f for f in os.listdir(folder_path)
             if os.path.splitext(f)[1].lower() in exts]

    results = []
    for fname in sorted(files):
        inp = os.path.join(folder_path, fname)
        out = os.path.join(output_folder, os.path.splitext(fname)[0] + ".jpg")
        try:
            results.append(process_product_image(inp, out))
        except Exception as e:
            print(f"  ERROR processing {fname}: {e}")

    return results
