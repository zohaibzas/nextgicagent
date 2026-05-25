const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageBreak, TabStopType, TabStopPosition,
  Footer, Header
} = require('docx');
const fs = require('fs');

// ── Color palette ─────────────────────────────────────────────────────────
const C = {
  brand:      "1A56DB",   // blue
  brandLight: "E8F0FE",   // light blue fill
  accent:     "0E9F6E",   // green (success)
  accentLight:"ECFDF5",
  warn:       "D97706",   // amber
  warnLight:  "FFFBEB",
  dark:       "111928",   // near black
  mid:        "6B7280",   // gray text
  border:     "D1D5DB",   // table border
  white:      "FFFFFF",
};

const border = { style: BorderStyle.SINGLE, size: 1, color: C.border };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// ── Helpers ───────────────────────────────────────────────────────────────

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.brand, space: 6 } },
    children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: C.brand })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: C.dark })]
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: C.mid })]
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 100 },
    children: [new TextRun({
      text,
      font: "Arial",
      size: 22,
      color: opts.color || C.dark,
      bold: opts.bold || false,
      italics: opts.italic || false,
    })]
  });
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, font: "Arial", size: 22, color: C.dark })]
  });
}

function numbered(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "numbers", level },
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, font: "Arial", size: 22, color: C.dark })]
  });
}

function spacer(lines = 1) {
  return Array.from({ length: lines }, () =>
    new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun("")] })
  );
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// Colored info box (no table, uses paragraph border)
function infoBox(label, text, color = C.brand, fillColor = C.brandLight) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [new TableCell({
          borders,
          width: { size: 9360, type: WidthType.DXA },
          shading: { fill: fillColor, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 180, right: 180 },
          children: [
            new Paragraph({
              spacing: { before: 0, after: 60 },
              children: [new TextRun({ text: label, font: "Arial", size: 20, bold: true, color })]
            }),
            new Paragraph({
              spacing: { before: 0, after: 0 },
              children: [new TextRun({ text, font: "Arial", size: 20, color: C.dark })]
            })
          ]
        })]
      })
    ]
  });
}

// Simple data table
function dataTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) =>
      new TableCell({
        borders,
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: C.brand, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: h, font: "Arial", size: 20, bold: true, color: C.white })]
        })]
      })
    )
  });

  const dataRows = rows.map((row, ri) =>
    new TableRow({
      children: row.map((cell, ci) =>
        new TableCell({
          borders,
          width: { size: colWidths[ci], type: WidthType.DXA },
          shading: { fill: ri % 2 === 0 ? C.white : "F9FAFB", type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({
            children: [new TextRun({ text: cell, font: "Arial", size: 20, color: C.dark })]
          })]
        })
      )
    })
  );

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows]
  });
}

// ── Document content ──────────────────────────────────────────────────────

const children = [

  // ── COVER ──────────────────────────────────────────────────────────────
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 2400, after: 200 },
    children: [new TextRun({ text: "NEXTGIC", font: "Arial", size: 52, bold: true, color: C.brand })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 120 },
    children: [new TextRun({ text: "Product Management Agent System", font: "Arial", size: 36, color: C.dark })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 800 },
    children: [new TextRun({ text: "Product Requirements Document  |  v1.0  |  2025", font: "Arial", size: 22, color: C.mid, italics: true })]
  }),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3120, 3120, 3120],
    rows: [new TableRow({
      children: [
        new TableCell({
          borders, width: { size: 3120, type: WidthType.DXA },
          shading: { fill: C.brandLight, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 120, right: 120 },
          children: [
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Status", font: "Arial", size: 18, bold: true, color: C.mid })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "In Development", font: "Arial", size: 20, bold: true, color: C.brand })] }),
          ]
        }),
        new TableCell({
          borders, width: { size: 3120, type: WidthType.DXA },
          shading: { fill: C.brandLight, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 120, right: 120 },
          children: [
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Version", font: "Arial", size: 18, bold: true, color: C.mid })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "1.0.0", font: "Arial", size: 20, bold: true, color: C.brand })] }),
          ]
        }),
        new TableCell({
          borders, width: { size: 3120, type: WidthType.DXA },
          shading: { fill: C.brandLight, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 120, right: 120 },
          children: [
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Owner", font: "Arial", size: 18, bold: true, color: C.mid })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Nextgic Dev Team", font: "Arial", size: 20, bold: true, color: C.brand })] }),
          ]
        }),
      ]
    })]
  }),

  pageBreak(),

  // ── SECTION 1: OVERVIEW ──────────────────────────────────────────────
  h1("1. Executive Overview"),

  body("Nextgic provides backend eCommerce support services, managing product listings and stock updates on behalf of clients who operate WooCommerce stores. Currently this entire workflow is handled manually by a team communicating through WhatsApp."),
  ...spacer(),
  body("This document defines the requirements, architecture, and workflow for an AI-powered multi-agent system that automates three core daily tasks: out-of-stock management, product duplication, and new product creation."),

  ...spacer(),
  infoBox(
    "Problem Statement",
    "Every day, team members receive WhatsApp messages from clients containing product screenshots, stock updates, and new product details. They then manually search WooCommerce, update stock statuses, duplicate products, and create new listings. This process is slow, error-prone, and does not scale.",
    C.warn,
    C.warnLight
  ),
  ...spacer(),
  infoBox(
    "Solution",
    "An automated agent system that reads WhatsApp messages and attached images, understands what action is required, and executes that action directly in WooCommerce — without any manual steps.",
    C.accent,
    C.accentLight
  ),

  ...spacer(2),

  // ── SECTION 2: GOALS ────────────────────────────────────────────────
  h1("2. Goals & Success Metrics"),

  h2("2.1 Primary Goals"),
  bullet("Eliminate manual product management steps currently done through WhatsApp"),
  bullet("Reduce processing time per task from 5-15 minutes to under 60 seconds"),
  bullet("Remove human error in product search, stock updates, and data entry"),
  bullet("Scale the team's capacity without adding headcount"),

  ...spacer(),
  h2("2.2 Success Metrics"),
  dataTable(
    ["Metric", "Current (Manual)", "Target (Automated)"],
    [
      ["Time per OOS update",     "5–10 min",  "< 30 seconds"],
      ["Time per duplication",    "10–20 min", "< 60 seconds"],
      ["Time per new product",    "20–30 min", "< 90 seconds"],
      ["Error rate (wrong SKU etc)", "~5%",    "< 1%"],
      ["Daily capacity (tasks)",  "20–40",     "200+"],
    ],
    [3400, 3000, 3000]
  ),

  ...spacer(2),

  // ── SECTION 3: STAKEHOLDERS ─────────────────────────────────────────
  h1("3. Stakeholders"),
  dataTable(
    ["Role", "Responsibility", "Interaction with System"],
    [
      ["Client",          "Sends stock and product updates",         "WhatsApp (images + text)"],
      ["Nextgic Team",    "Monitors, reviews, handles exceptions",   "WhatsApp replies + /logs API"],
      ["Developer",       "Maintains and deploys the system",        "Docker, .env, codebase"],
      ["WooCommerce Store","Receives automated product changes",     "REST API (automated)"],
    ],
    [2600, 3600, 3200]
  ),

  pageBreak(),

  // ── SECTION 4: SYSTEM ARCHITECTURE ─────────────────────────────────
  h1("4. System Architecture"),

  h2("4.1 Technology Stack"),
  dataTable(
    ["Layer", "Technology", "Purpose"],
    [
      ["Input",           "whatsapp-web.js (Node.js)",    "Listens to WhatsApp group messages"],
      ["API Backend",     "FastAPI (Python)",              "Receives images, routes to agents"],
      ["AI Vision",       "GPT-4o (OpenAI)",              "Reads screenshots, extracts data"],
      ["Agent Logic",     "Python (custom agents)",        "Executes business rules"],
      ["Image Processing","Pillow + psd-tools",            "Composes product images in template"],
      ["Product API",     "WooCommerce REST API v3",       "Creates, updates, duplicates products"],
      ["Database",        "SQLite → PostgreSQL",           "Job logs, deduplication, cache"],
      ["Auth",            "API Key Middleware (FastAPI)",   "Secures all backend routes"],
      ["Logging",         "Python logging (rotating files)","Audit trail, debugging"],
      ["Deployment",      "Docker + docker-compose",       "Reproducible, portable deployment"],
    ],
    [2400, 3000, 3960]
  ),

  ...spacer(),
  h2("4.2 High-Level Architecture"),

  body("The system follows a pipeline architecture with clear separation between input, intelligence, and execution layers:", { bold: true }),
  ...spacer(),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders,
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: "F3F4F6", type: ShadingType.CLEAR },
        margins: { top: 180, bottom: 180, left: 240, right: 240 },
        children: [
          new Paragraph({ spacing: { before: 60, after: 60 }, children: [new TextRun({ text: "CLIENT (WhatsApp)", font: "Courier New", size: 20, bold: true, color: C.brand })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  Sends: screenshot/product image + text", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "          \u2193", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "WHATSAPP BOT (whatsapp-web.js)", font: "Courier New", size: 20, bold: true, color: C.brand })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  Collects images (current + quoted + recent 60s)", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  POSTs to Python API with X-API-Key header", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "          \u2193", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "FASTAPI BACKEND (main.py)", font: "Courier New", size: 20, bold: true, color: C.brand })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  Auth middleware validates API key", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  Saves images to temp dir", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  Enqueues task (sync now / Celery later)", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "          \u2193", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "INTAKE AGENT", font: "Courier New", size: 20, bold: true, color: C.brand })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  GPT-4o reads image + text", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "  Classifies: oos | duplicate | new_product", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "     \u2193           \u2193               \u2193", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "OOS AGENT   DUPLICATE AGENT   NEW PRODUCT AGENT", font: "Courier New", size: 20, bold: true, color: C.accent })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "          \u2193", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "WOOCOMMERCE REST API", font: "Courier New", size: 20, bold: true, color: C.brand })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "          \u2193", font: "Courier New", size: 18, color: C.mid })] }),
          new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: "WHATSAPP REPLY (confirmation or error)", font: "Courier New", size: 20, bold: true, color: C.accent })] }),
        ]
      })]
    })]
  }),

  pageBreak(),

  // ── SECTION 5: AGENTS ─────────────────────────────────────────────────
  h1("5. Agent Definitions"),

  // Intake
  h2("5.1 Intake Agent"),
  body("The entry point for all tasks. Receives all images and text from a WhatsApp message and determines what action the client is requesting."),
  ...spacer(),
  dataTable(
    ["Property", "Detail"],
    [
      ["Input",       "1–5 images + optional text message"],
      ["AI Model",    "GPT-4o Vision"],
      ["Output",      "Task classification: oos | duplicate | new_product | unknown"],
      ["Confidence",  "Minimum 60% required to proceed; below that returns error"],
      ["Dedup",       "Checks DB for WhatsApp message ID before processing"],
    ],
    [3000, 6360]
  ),

  ...spacer(),
  h2("5.2 OOS Agent (Out-of-Stock Manager)"),
  body("Handles stock status changes. The client sends a screenshot of a product page showing an 'OUT OF STOCK' badge, or a product they want marked back in stock. The agent reads the product name, finds it in WooCommerce, and updates the stock status."),
  ...spacer(),
  dataTable(
    ["Property", "Detail"],
    [
      ["Input",          "Screenshot with OUT OF STOCK badge or in-stock product"],
      ["Text override",  "If message contains 'Instock' or 'OOS', overrides visual badge"],
      ["Search method",  "WooCommerce API search + rapidfuzz fuzzy matching (75% threshold)"],
      ["API call",       "PUT /products/{id} with stock_status: outofstock | instock"],
      ["Cache",          "Product name → ID cached in DB for 60 minutes"],
      ["Reply",          "Confirms product name and new stock status"],
    ],
    [2800, 6560]
  ),

  ...spacer(),
  h2("5.3 Duplicate Agent"),
  body("Handles product duplication. The client sends a screenshot of a source product and a list of target phone models with new SKUs. The agent creates one duplicate per model, updating the title, SKU, URL slug, and phone model attribute on each."),
  ...spacer(),
  dataTable(
    ["Property", "Detail"],
    [
      ["Input",               "Screenshot of source product + target models + new SKUs"],
      ["Source lookup",       "Fuzzy search in WooCommerce by product name"],
      ["Attribute detection", "Reads source product attributes dynamically — not hardcoded"],
      ["Per duplicate",       "New title, new SKU, new slug, updated phone model attribute"],
      ["Batch support",       "Creates N duplicates in one run (e.g. S26, S26+, S26 Ultra)"],
      ["API calls",           "GET /products/{id} then POST /products per duplicate"],
      ["Reply",               "Reports N created / N failed with product IDs"],
    ],
    [2800, 6560]
  ),

  ...spacer(),
  h2("5.4 New Product Agent"),
  body("Handles complete new product creation end-to-end. Classifies each image as a screenshot (for extracting text details) or a clean product photo (for processing through the template). Processes the product image, creates WooCommerce categories if needed, uploads everything, and publishes the product."),
  ...spacer(),
  dataTable(
    ["Property", "Detail"],
    [
      ["Input",             "Product photo + screenshot with name/price/SKU/category"],
      ["Image classifier",  "GPT-4o: SCREENSHOT vs PRODUCT on each image"],
      ["Image processing",  "Pillow: places product in 800x800 PSD template, 80px padding, centered"],
      ["Text extraction",   "GPT-4o reads name, price, SKU, category path from screenshot"],
      ["Text fallback",     "Regex parser on raw message text for missing fields"],
      ["Category handling", "Creates full category path if not exists (e.g. Accessories/gadgets/cases)"],
      ["Image upload",      "WordPress media API, returns attachment ID"],
      ["API calls",         "POST /products/categories, POST /media, POST /products"],
      ["Reply",             "Product name, ID, permalink on success"],
    ],
    [2800, 6560]
  ),

  pageBreak(),

  // ── SECTION 6: DETAILED WORKFLOWS ───────────────────────────────────
  h1("6. Detailed Workflows"),

  h2("6.1 Task 1 — Out-of-Stock / In-Stock Update"),
  ...spacer(),

  dataTable(
    ["Step", "Actor", "Action", "Output"],
    [
      ["1", "Client",        "Sends WhatsApp message with product screenshot",            "Image in Dev Team group"],
      ["2", "WhatsApp Bot",  "Detects image in target group, downloads it",              "Image file on disk"],
      ["3", "WhatsApp Bot",  "POSTs image + text to FastAPI /process with API key",       "HTTP request"],
      ["4", "Auth Middleware","Validates X-API-Key header",                               "Allowed or 401"],
      ["5", "Intake Agent",  "GPT-4o classifies as 'oos' task",                          "task = 'oos'"],
      ["6", "OOS Agent",     "GPT-4o extracts product name and action from screenshot",   "name, action"],
      ["7", "OOS Agent",     "Checks product cache in DB",                               "Cache hit or miss"],
      ["8", "OOS Agent",     "Searches WooCommerce API by name with fuzzy matching",      "Product ID"],
      ["9", "OOS Agent",     "Updates stock_status via PUT /products/{id}",              "WooCommerce updated"],
      ["10","DB",            "Logs job result to job_log table",                          "Row in DB"],
      ["11","WhatsApp Bot",  "Sends confirmation reply to group",                         "Reply message"],
    ],
    [600, 1800, 4200, 2760]
  ),

  ...spacer(2),
  h2("6.2 Task 2 — Product Duplication"),
  ...spacer(),

  dataTable(
    ["Step", "Actor", "Action", "Output"],
    [
      ["1", "Client",       "Sends screenshot of source product + text with models and SKUs", "Image + text"],
      ["2", "WhatsApp Bot", "Downloads image, POSTs to /process",                             "HTTP request"],
      ["3", "Intake Agent", "GPT-4o classifies as 'duplicate' task",                         "task = 'duplicate'"],
      ["4", "Dup. Agent",   "GPT-4o extracts source product name + list of (model, SKU)",     "Structured data"],
      ["5", "Dup. Agent",   "Searches WooCommerce for source product",                        "Source product ID"],
      ["6", "Dup. Agent",   "Fetches full product data including attributes",                  "Full product JSON"],
      ["7", "Dup. Agent",   "Detects phone model attribute name dynamically",                  "Attribute name"],
      ["8", "Dup. Agent",   "For each duplicate: clones product, updates title/SKU/slug/attr","N new products"],
      ["9", "DB",           "Logs job result",                                                "Row in DB"],
      ["10","WhatsApp Bot", "Sends reply: N created / N failed",                              "Reply message"],
    ],
    [600, 1800, 4200, 2760]
  ),

  ...spacer(2),
  h2("6.3 Task 3 — New Product Creation"),
  ...spacer(),

  dataTable(
    ["Step", "Actor", "Action", "Output"],
    [
      ["1",  "Client",       "Sends product photo + text with name, price, SKU, category", "Images + text"],
      ["2",  "WhatsApp Bot", "Collects all images from message, quoted messages, last 60s", "Image list"],
      ["3",  "WhatsApp Bot", "POSTs all images + text to /process",                         "HTTP request"],
      ["4",  "Intake Agent", "GPT-4o classifies as 'new_product'",                          "task = 'new_product'"],
      ["5",  "NP Agent",     "Classifies each image: SCREENSHOT or PRODUCT",                "Two buckets"],
      ["6",  "NP Agent",     "GPT-4o extracts name, price, SKU, category from screenshot",  "Product fields"],
      ["7",  "NP Agent",     "Regex fallback fills any missing fields from text",            "Complete fields"],
      ["8",  "NP Agent",     "Pillow processes product image into 800x800 template",         "Processed JPEG"],
      ["9",  "NP Agent",     "Creates WooCommerce categories for full path if not exists",   "Category IDs"],
      ["10", "NP Agent",     "Uploads processed image to WordPress media library",           "Media ID + URL"],
      ["11", "NP Agent",     "Creates and publishes product via POST /products",             "Product ID"],
      ["12", "DB",           "Logs job result",                                              "Row in DB"],
      ["13", "WhatsApp Bot", "Sends reply: product name, ID, permalink",                     "Reply message"],
    ],
    [600, 1800, 4200, 2760]
  ),

  pageBreak(),

  // ── SECTION 7: DATA & PERSISTENCE ────────────────────────────────────
  h1("7. Data & Persistence"),

  h2("7.1 Database Tables"),
  body("The system uses SQLite by default. Switch to PostgreSQL by changing DATABASE_URL in .env. All tables are created automatically on startup."),
  ...spacer(),

  dataTable(
    ["Table", "Purpose", "Key Fields"],
    [
      ["job_log",           "Audit log of every task",                  "task_type, status, duration_sec, result_json, error_msg"],
      ["processed_message", "Deduplication — prevents double-processing","message_id (unique), task_type, success"],
      ["product_cache",     "Name-to-ID cache (60 min TTL)",            "product_name (unique), product_id, cached_at"],
    ],
    [2400, 3200, 3760]
  ),

  ...spacer(),
  h2("7.2 Image Lifecycle"),
  numbered("Client sends image on WhatsApp"),
  numbered("Bot downloads to temp_uploads/ directory"),
  numbered("Agent reads and processes the image"),
  numbered("Processed image saved to processed_images/"),
  numbered("Image uploaded to WordPress media library"),
  numbered("Temp and processed files deleted"),

  ...spacer(),
  h2("7.3 Image Template Specification"),
  dataTable(
    ["Property", "Value"],
    [
      ["Canvas size",   "800 x 800 pixels"],
      ["Resolution",    "72 DPI"],
      ["Background",    "White (#FFFFFF)"],
      ["Padding",       "80px all sides (640x640 usable area)"],
      ["Product fit",   "Scaled to fit within padding, aspect ratio preserved"],
      ["Alignment",     "Centered horizontally and vertically"],
      ["Output format", "JPEG, quality 95"],
      ["Template file", "canvas-Igen__1_.psd (smart object zone auto-read)"],
    ],
    [3000, 6360]
  ),

  pageBreak(),

  // ── SECTION 8: SECURITY ──────────────────────────────────────────────
  h1("8. Security"),

  dataTable(
    ["Concern", "Implementation", "Status"],
    [
      ["API Authentication",    "X-API-Key header required on all routes",          "Done"],
      ["Key generation",        "python -c \"import secrets; print(secrets.token_hex(32))\"", "Done"],
      ["Public routes",         "/health exempt from auth",                         "Done"],
      ["WhatsApp number",       "Use secondary number, not main business number",   "Operational"],
      ["Credentials",           "All secrets in .env, never committed to git",      "Done"],
      ["DB exposure",           "PostgreSQL not exposed externally in Docker",       "Done"],
      ["Redis queue (future)",  "Internal Docker network only",                     "Planned"],
      ["WooCommerce API keys",  "Read/Write scope, can be scoped per key",          "Operational"],
    ],
    [2800, 4200, 2360]
  ),

  pageBreak(),

  // ── SECTION 9: DEPLOYMENT ───────────────────────────────────────────
  h1("9. Deployment"),

  h2("9.1 Local / Development"),
  numbered("Copy .env.example to .env and fill in credentials"),
  numbered("pip install -r requirements.txt"),
  numbered("cd whatsapp && npm install"),
  numbered("python main.py <screenshot.jpg> (manual test)"),
  numbered("uvicorn main:app --port 8000 (start API)"),
  numbered("node whatsapp/bot.js (start WhatsApp listener)"),

  ...spacer(),
  h2("9.2 Production (Docker)"),
  numbered("Fill in .env with all production credentials"),
  numbered("docker compose up -d"),
  numbered("docker compose logs -f whatsapp (scan QR code on first run)"),
  numbered("docker compose logs -f agent (monitor agent activity)"),

  ...spacer(),
  h2("9.3 Docker Services"),
  dataTable(
    ["Service", "Image", "Port", "Status"],
    [
      ["agent",          "Custom Python build",    "8000",  "Always on"],
      ["whatsapp",       "node:20-slim",           "None",  "Always on"],
      ["db",             "postgres:16-alpine",     "5432",  "Always on"],
      ["redis",          "redis:7-alpine",         "6379",  "Ready (activate with Celery)"],
      ["celery_worker",  "Custom Python build",    "None",  "Commented out (activate later)"],
    ],
    [2400, 2800, 1600, 2560]
  ),

  pageBreak(),

  // ── SECTION 10: FUTURE ROADMAP ──────────────────────────────────────
  h1("10. Future Roadmap"),

  h2("Phase 1 — Current (v1.0)"),
  bullet("SQLite database with job logs, dedup, product cache"),
  bullet("API key authentication"),
  bullet("Structured file logging with rotation"),
  bullet("Docker + docker-compose deployment"),
  bullet("Synchronous task execution"),
  bullet("whatsapp-web.js for WhatsApp integration"),

  ...spacer(),
  h2("Phase 2 — Next (v1.5)"),
  bullet("Switch to PostgreSQL (change one env var)"),
  bullet("Activate Redis + Celery queue (uncomment in docker-compose)"),
  bullet("Background removal for product images (rembg library)"),
  bullet("Admin dashboard to view job_log via web UI"),
  bullet("/logs endpoint already built — UI layer only needed"),

  ...spacer(),
  h2("Phase 3 — Scale (v2.0)"),
  bullet("Migrate WhatsApp integration to Evolution API (production-grade)"),
  bullet("Migrate agent logic to CrewAI framework"),
  bullet("Multi-client support (multiple WooCommerce stores)"),
  bullet("Automated retry logic for failed tasks"),
  bullet("Slack/email alerts for errors"),

  ...spacer(2),

  // ── SECTION 11: KNOWN LIMITATIONS ──────────────────────────────────
  h1("11. Known Limitations"),

  infoBox("whatsapp-web.js", "Unofficial library. Can break when WhatsApp updates their web app. Suitable for testing and small teams. Migrate to Evolution API before scaling to high message volumes.", C.warn, C.warnLight),
  ...spacer(),
  infoBox("Synchronous processing", "Currently tasks block the API response. Two messages arriving simultaneously may queue behind each other. Resolved in Phase 2 by activating Celery.", C.warn, C.warnLight),
  ...spacer(),
  infoBox("GPT-4o cost", "Each task requires 1–3 GPT-4o API calls. Estimated cost is $0.01–0.05 per task depending on image size. At 100 tasks/day this is under $5/day.", C.brand, C.brandLight),
  ...spacer(),
  infoBox("Product name matching", "Fuzzy matching threshold is 75%. Very short or abbreviated product names may fail to match. Team should use consistent naming conventions.", C.brand, C.brandLight),

  pageBreak(),

  // ── SECTION 12: FILE STRUCTURE ──────────────────────────────────────
  h1("12. Project File Structure"),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders,
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: "F3F4F6", type: ShadingType.CLEAR },
        margins: { top: 180, bottom: 180, left: 240, right: 240 },
        children: [
          ["nextgic-agent/",                     true,  0],
          ["├── agents/",                         false, 0],
          ["│   ├── intake_agent.py",             false, 1],
          ["│   ├── oos_agent.py",                false, 1],
          ["│   ├── duplicate_agent.py",          false, 1],
          ["│   └── new_product_agent.py",        false, 1],
          ["├── tools/",                          false, 0],
          ["│   ├── woocommerce.py",              false, 1],
          ["│   ├── vision.py",                   false, 1],
          ["│   └── image_processor.py",          false, 1],
          ["├── db/",                             false, 0],
          ["│   ├── database.py",                 false, 1],
          ["│   └── helpers.py",                  false, 1],
          ["├── middleware/",                      false, 0],
          ["│   └── auth.py",                     false, 1],
          ["├── queue/",                          false, 0],
          ["│   ├── worker.py",                   false, 1],
          ["│   └── tasks.py",                    false, 1],
          ["├── whatsapp/",                       false, 0],
          ["│   ├── bot.js",                      false, 1],
          ["│   └── package.json",                false, 1],
          ["├── canvas-Igen__1_.psd",             false, 0],
          ["├── main.py",                         false, 0],
          ["├── logger.py",                       false, 0],
          ["├── config.py",                       false, 0],
          ["├── requirements.txt",                false, 0],
          ["├── Dockerfile",                      false, 0],
          ["├── docker-compose.yml",              false, 0],
          ["└── .env.example",                    false, 0],
        ].map(([text, bold, indent]) =>
          new Paragraph({
            spacing: { before: 20, after: 20 },
            indent: { left: indent * 240 },
            children: [new TextRun({ text, font: "Courier New", size: 18, bold, color: bold ? C.brand : C.dark })]
          })
        )
      })]
    })]
  }),

  ...spacer(2),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 400, after: 0 },
    children: [new TextRun({ text: "— End of Document —", font: "Arial", size: 20, color: C.mid, italics: true })]
  }),
];

// ── Build document ────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
        ]
      },
      {
        reference: "numbers",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ]
      }
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: C.brand },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: C.dark },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: C.mid },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: C.brand, space: 6 } },
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Nextgic Product Agent  |  Confidential", font: "Arial", size: 18, color: C.mid }),
          ]
        })]
      })
    },
    children,
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('./Nextgic_Product_Agent_PRD.docx', buffer);
  console.log('Done: Nextgic_Product_Agent_PRD.docx');
});
