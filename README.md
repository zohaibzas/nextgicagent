# Nextgic Product Agent

Automates WooCommerce product management from WhatsApp messages.
Handles: Out-of-Stock updates, Product Duplication, New Product creation.

---

## Folder Structure

```
nextgic-agent/
├── agents/
│   ├── intake_agent.py       ← Classifies task, routes to correct agent
│   ├── oos_agent.py          ← Marks products in/out of stock
│   ├── duplicate_agent.py    ← Duplicates products with new SKUs
│   └── new_product_agent.py  ← Creates new products end-to-end
├── tools/
│   ├── woocommerce.py        ← All WooCommerce API operations
│   ├── vision.py             ← GPT-4o reads WhatsApp screenshots
│   └── image_processor.py   ← Processes product images (PSD template)
├── whatsapp/
│   ├── bot.js                ← WhatsApp listener (whatsapp-web.js)
│   └── package.json          ← Node dependencies (pinned versions)
├── canvas-Igen__1_.psd       ← Your PSD template (included)
├── config.py                 ← Credentials loader
├── main.py                   ← FastAPI backend + manual test runner
├── requirements.txt          ← Python dependencies (pinned versions)
└── .env                      ← Your credentials (copy from .env.example)
```

---

## Setup (Step by Step)

### Step 1 — Python environment

```bash
pip install -r requirements.txt
```

### Step 2 — Fill in credentials

```bash
cp .env.example .env
# Edit .env with your real values
```

You need:
- **WooCommerce REST API keys** — WooCommerce → Settings → Advanced → REST API → Add Key (Read/Write)
- **OpenAI API key** — https://platform.openai.com/api-keys

### Step 3 — Start the Python backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 4 — Set up WhatsApp bot

```bash
cd whatsapp
npm install
node bot.js
```

Scan the QR code with your secondary WhatsApp number.

### Step 5 — Keep both running 24/7 (recommended)

```bash
npm install -g pm2
pm2 start whatsapp/bot.js --name "whatsapp-bot"
pm2 start "uvicorn main:app --port 8000" --name "agent-backend"
pm2 save
pm2 startup
```

---

## Testing Without WhatsApp

Test any task directly from the command line before connecting WhatsApp.
Always do this first.

```bash
# Test OOS update
python main.py ./test_images/oos_screenshot.jpg "Instock"

# Test duplication
python main.py ./test_images/duplicate_screenshot.jpg

# Test new product (screenshot only)
python main.py ./test_images/new_product_screenshot.jpg

# Test new product (screenshot + separate product photo)
python main.py ./test_images/new_product_screenshot.jpg ./test_images/product_photo.jpg
```

---

## How It Works

```
WhatsApp Group Message (image + text)
            ↓
    whatsapp/bot.js
    Collects all images (main + quoted + recent),
    POSTs to Python API
            ↓
    main.py (FastAPI /process endpoint)
    Saves images, calls intake_agent
            ↓
    intake_agent.py
    GPT-4o classifies: oos / duplicate / new_product
            ↓
    ┌──────────────────────────────────┐
    │              │                   │
oos_agent   duplicate_agent   new_product_agent
    │              │                   │
    │    Detect model attribute    Classify each image:
    │    dynamically from source   screenshot vs product photo
    │    product (not hardcoded)   Extract details from screenshot
    │              │               Process product image
    │              │               Upload + create product
    └──────────────┴───────────────────┘
            ↓
    WooCommerce REST API
            ↓
    Reply sent back to WhatsApp group
```

---

## What Each Agent Does

### OOS Agent
- GPT-4o reads screenshot → extracts product name + action (instock/outofstock)
- Text message (e.g. "Instock") can override the visual badge
- Searches WooCommerce with fuzzy matching (handles slight name variations)
- Updates stock status via REST API

### Duplicate Agent
- GPT-4o reads screenshot → extracts source product + list of (model, SKU) pairs
- Finds source product in WooCommerce (with fuzzy matching)
- Fetches full product data to detect the phone model attribute dynamically
- Creates N duplicates, each with new title, SKU, slug, and model attribute
- Does NOT hardcode attribute names — works with any store taxonomy

### New Product Agent
- Receives all images from the message
- Asks GPT-4o to classify each: SCREENSHOT vs PRODUCT (clean photo)
- Extracts product details (name, price, SKU, category) from the screenshot
- Falls back to text message if any field is missing
- Processes the clean product image through your PSD template
- Creates or finds WooCommerce categories (full path support)
- Uploads image and creates product

---

## WhatsApp Message Formats

**OOS/Instock:**
Screenshot of product card (with OUT OF STOCK badge) + optional text "Instock"

**Duplicate:**
Screenshot of source product page + text listing target models and SKUs

**New Product:**
Product photo + text with: product name, price, SKU, Location/category
(can be split across two messages sent within 60 seconds)

---

## Important Notes

- Use a **secondary WhatsApp number** for the bot, not your main business number
- The bot monitors the **"Dev Team (Nextgic)"** group — change `TARGET_GROUP` in bot.js if needed
- The bot collects images from the current message, quoted/replied messages, and any images sent in the last 60 seconds in the same group
- GPT-4o vision costs roughly $0.01–0.03 per task processed
- WooCommerce REST API key must have **Read/Write** permissions
