"""
config.py — All credentials and settings
Fill in your values before running.
"""

import os
from dotenv import load_dotenv

# Load .env relative to the config file directory
config_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(config_dir, ".env"))

# ── WooCommerce ───────────────────────────────────────────────────────────────
WC_URL             = os.getenv("WC_URL", "https://yourdomain.com")
WC_CONSUMER_KEY    = os.getenv("WC_CONSUMER_KEY", "ck_xxxxxxxxxxxxxxxx")
WC_CONSUMER_SECRET = os.getenv("WC_CONSUMER_SECRET", "cs_xxxxxxxxxxxxxxxx")
WP_USERNAME        = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD    = os.getenv("WP_APP_PASSWORD", "")

# ── NVIDIA NIM API (replaces OpenAI) ──────────────────────────────────────────
NVIDIA_API_KEY     = os.getenv("NVIDIA_API_KEY", "nvapi-xxxxxxxxxxxxxxxx")
NVIDIA_BASE_URL    = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_VISION_MODEL = os.getenv("NVIDIA_VISION_MODEL", "meta/llama-3.2-90b-vision-instruct")

# ── Image Processing ──────────────────────────────────────────────────────────
PSD_TEMPLATE_PATH  = os.getenv("PSD_TEMPLATE_PATH", "./canvas-Igen__1_.psd")
PROCESSED_DIR      = os.getenv("PROCESSED_DIR", "./processed_images/")

# ── Agent settings ────────────────────────────────────────────────────────────
FUZZY_MATCH_THRESHOLD = 75   # % similarity for product name matching (0-100)
