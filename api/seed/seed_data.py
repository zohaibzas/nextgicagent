"""
api/seed/seed_data.py
Generates realistic mock data for local development.
Run: python -m api.seed.seed_data
"""

import random
import json
import uuid
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.models.dashboard_models import (
    Base, WorkflowRun, WorkflowStep, AIRequest, ErrorEvent,
    QueueJob, MediaAsset, WooCommerceOp, SystemLog, Alert,
    DashboardUser, WebhookEvent, SystemSetting, init_dashboard_db
)
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Config ──────────────────────────────────────────────────────────────────

AGENTS = ["intake_agent", "oos_agent", "duplicate_agent", "new_product_agent"]
TASK_TYPES = ["oos", "duplicate", "new_product", "unknown"]
STATUSES = ["success", "failed", "running", "retrying", "queued", "cancelled"]
STATUS_WEIGHTS = [0.72, 0.12, 0.05, 0.05, 0.04, 0.02]

WC_OPS = ["product_create", "product_update", "product_search",
          "product_duplicate", "stock_update", "category_create", "image_upload"]
ERROR_TYPES = ["gpt_failure", "wc_api_error", "queue_failure", "image_failure",
               "auth_failure", "validation_error", "timeout"]
SEVERITIES = ["critical", "error", "warning", "info"]
LOG_LEVELS = ["DEBUG", "INFO", "INFO", "INFO", "WARN", "ERROR"]

STEP_TEMPLATES = {
    "oos": [
        ("whatsapp_receive", "WhatsApp message received"),
        ("image_download", "Image downloaded"),
        ("gpt_classify", "GPT-4o classification"),
        ("wc_search", "WooCommerce product search"),
        ("stock_update", "Stock status updated"),
        ("confirmation_send", "Confirmation sent"),
    ],
    "duplicate": [
        ("whatsapp_receive", "WhatsApp message received"),
        ("image_download", "Image downloaded"),
        ("gpt_classify", "GPT-4o classification"),
        ("gpt_extract", "Extract duplication data"),
        ("wc_search", "Source product found"),
        ("wc_create", "Duplicates created"),
        ("confirmation_send", "Confirmation sent"),
    ],
    "new_product": [
        ("whatsapp_receive", "WhatsApp message received"),
        ("image_download", "Images downloaded"),
        ("gpt_classify", "GPT-4o classification"),
        ("image_classify", "Image type classification"),
        ("gpt_extract", "Extract product data"),
        ("image_process", "PSD template processing"),
        ("wc_category", "Category resolved"),
        ("wc_create", "Product created in WooCommerce"),
        ("image_upload", "Product image uploaded"),
        ("confirmation_send", "Confirmation sent"),
    ],
}

PRODUCT_NAMES = [
    "Elegant Flower MagSafe Green – iPhone 17 Pro",
    "Galaxy S26 Ultra Leather Case – Midnight Black",
    "Pixel 9 Pro Bumper Case – Coral Red",
    "iPhone 16 Pro Max Silicone Case – Storm Blue",
    "Samsung A55 Clear Case – Crystal",
    "OnePlus 13 Rugged Case – Military Green",
    "Xiaomi 14 Ultra PSD Template Phone Case",
    "iPhone 15 Plus Wallet Case – Brown Leather",
]

PHONE_MODELS = [
    "iPhone 17 Pro", "iPhone 17 Pro Max", "Samsung S26", "Samsung S26 Ultra",
    "Pixel 9", "Pixel 9 Pro", "OnePlus 13", "Xiaomi 14"
]

STACK_TRACES = [
    """Traceback (most recent call last):
  File "/app/agents/oos_agent.py", line 41, in run
    product = wc.search_product(product_name)
  File "/app/tools/woocommerce.py", line 89, in search_product
    response = self.wcapi.get("products", params=params)
requests.exceptions.Timeout: HTTPSConnectionPool(host='store.example.com', port=443): Read timed out. (read timeout=30)""",
    """Traceback (most recent call last):
  File "/app/queue/tasks.py", line 48, in _process_whatsapp_message
    result = intake_agent.run(image_paths=image_paths, text_message=text_message)
  File "/app/agents/intake_agent.py", line 38, in run
    classification = vision.classify_task(primary_image, text_message)
  File "/app/tools/vision.py", line 27, in ask_vision
    response = client.chat.completions.create(...)
openai.APIError: 503 Service Unavailable""",
    """json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  Response was: <html>Error 429 Too Many Requests</html>""",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def rand_dt(days_back: int = 30) -> datetime:
    return datetime.utcnow() - timedelta(
        days=random.uniform(0, days_back),
        hours=random.uniform(0, 24),
        minutes=random.uniform(0, 60),
    )

def rand_duration(min_ms=200, max_ms=8000):
    return random.randint(min_ms, max_ms)


# ── Seed Functions ────────────────────────────────────────────────────────────

def seed_users(session):
    print("  → Seeding users...")
    users = [
        {"email": "admin@nextgic.ai", "name": "Admin User", "role": "admin", "password": "admin123"},
        {"email": "operator@nextgic.ai", "name": "Operations Lead", "role": "operator", "password": "operator123"},
        {"email": "dev@nextgic.ai", "name": "Developer", "role": "developer", "password": "dev123"},
        {"email": "viewer@nextgic.ai", "name": "View Only", "role": "viewer", "password": "viewer123"},
    ]
    for u in users:
        if not session.query(DashboardUser).filter_by(email=u["email"]).first():
            user = DashboardUser(
                email=u["email"],
                name=u["name"],
                role=u["role"],
                password_hash=pwd_ctx.hash(u["password"]),
                is_active=True,
                last_login=datetime.utcnow() - timedelta(hours=random.uniform(0, 48)),
            )
            session.add(user)
    session.commit()
    print("    ✓ Users seeded (admin@nextgic.ai / admin123)")


def seed_settings(session):
    print("  → Seeding settings...")
    settings = [
        ("openai_model", "gpt-4o", "Default OpenAI model", False),
        ("wc_url", "https://store.example.com", "WooCommerce store URL", False),
        ("max_retries", "3", "Maximum task retry attempts", False),
        ("alert_failure_threshold", "0.20", "Alert when failure rate exceeds this %", False),
        ("alert_queue_depth", "50", "Alert when queue depth exceeds this", False),
        ("alert_ai_cost_daily", "10.00", "Alert when daily AI cost exceeds $", False),
        ("fuzzy_match_threshold", "75", "Product name fuzzy match threshold", False),
    ]
    for key, value, desc, secret in settings:
        if not session.query(SystemSetting).filter_by(key=key).first():
            session.add(SystemSetting(key=key, value=value, description=desc, is_secret=secret))
    session.commit()


def seed_workflows(session, count=500):
    print(f"  → Seeding {count} workflow runs...")
    runs = []
    for i in range(count):
        task = random.choice(TASK_TYPES)
        agent = {"oos": "oos_agent", "duplicate": "duplicate_agent",
                 "new_product": "new_product_agent", "unknown": "intake_agent"}[task]
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        started = rand_dt(30)
        duration = rand_duration(500, 12000) if status in ("success", "failed", "retrying") else None
        completed = started + timedelta(milliseconds=duration) if duration else None

        product = random.choice(PRODUCT_NAMES)
        wc_id = random.randint(100, 9999) if status == "success" else None

        run = WorkflowRun(
            run_id=str(uuid.uuid4()),
            agent_name=agent,
            task_type=task,
            status=status,
            started_at=started,
            completed_at=completed,
            duration_ms=duration,
            retry_count=random.randint(0, 3) if status in ("retrying", "failed") else 0,
            whatsapp_msg_id=f"WA_{uuid.uuid4().hex[:16]}",
            user_phone=f"+1555{random.randint(1000000, 9999999)}",
            wc_product_id=wc_id,
            input_data=json.dumps({"product": product, "task": task}),
            output_data=json.dumps({"success": status == "success", "product_id": wc_id}) if status == "success" else None,
            error_msg="WooCommerce API timeout" if status == "failed" else None,
        )
        runs.append(run)

    session.add_all(runs)
    session.flush()

    # Add steps
    print("  → Adding workflow steps...")
    for run in runs:
        steps_template = STEP_TEMPLATES.get(run.task_type, STEP_TEMPLATES["oos"])
        run_status = run.status
        t = run.started_at
        for order, (step_type, step_name) in enumerate(steps_template):
            step_dur = rand_duration(50, 3000)
            t_end = t + timedelta(milliseconds=step_dur)
            # Determine step status based on run status
            if run_status == "success":
                step_status = "success"
            elif run_status == "failed" and order == len(steps_template) - 2:
                step_status = "failed"
            elif run_status == "failed" and order < len(steps_template) - 2:
                step_status = "success"
            else:
                step_status = "success" if order < 3 else "pending"

            step = WorkflowStep(
                workflow_run_id=run.id,
                step_name=step_name,
                step_order=order,
                status=step_status,
                started_at=t,
                completed_at=t_end if step_status in ("success", "failed") else None,
                duration_ms=step_dur if step_status in ("success", "failed") else None,
                step_type=step_type,
                input_data=json.dumps({"step": step_name}),
                output_data=json.dumps({"ok": True}) if step_status == "success" else None,
                error_data=json.dumps({"error": "API timeout"}) if step_status == "failed" else None,
            )
            session.add(step)
            t = t_end

    session.commit()
    print(f"    ✓ {count} workflows + steps seeded")
    return runs


def seed_ai_requests(session, runs):
    print(f"  → Seeding AI requests...")
    MODELS = ["gpt-4o", "gpt-4o-mini", "meta/llama-3.2-90b-vision-instruct"]
    ai_reqs = []
    for run in runs:
        # Each workflow makes 1-4 AI calls
        for _ in range(random.randint(1, 4)):
            model = random.choice(MODELS)
            tokens_p = random.randint(200, 800)
            tokens_c = random.randint(50, 300)
            # GPT-4o: ~$5/1M input, $15/1M output
            cost = (tokens_p * 0.000005) + (tokens_c * 0.000015)
            ai_reqs.append(AIRequest(
                workflow_run_id=run.id,
                model=model,
                prompt_tokens=tokens_p,
                completion_tokens=tokens_c,
                total_tokens=tokens_p + tokens_c,
                cost_usd=round(cost, 6),
                latency_ms=random.randint(300, 4000),
                success=random.random() > 0.05,
                request_type=random.choice(["classify", "extract", "vision"]),
                created_at=run.started_at + timedelta(milliseconds=random.randint(100, 2000)),
            ))
    session.add_all(ai_reqs)
    session.commit()
    print(f"    ✓ {len(ai_reqs)} AI requests seeded")


def seed_errors(session, runs):
    print("  → Seeding error events...")
    failed_runs = [r for r in runs if r.status in ("failed", "retrying")]
    errors = []
    for run in failed_runs:
        errors.append(ErrorEvent(
            workflow_run_id=run.id,
            error_type=random.choice(ERROR_TYPES),
            severity=random.choices(["critical", "error", "warning"], weights=[0.1, 0.6, 0.3])[0],
            title=f"Error in {run.agent_name}",
            message=random.choice([
                "WooCommerce API returned 503",
                "GPT response could not be parsed as JSON",
                "Image download failed: connection reset",
                "Product not found in WooCommerce: 'Samsung Ultra Case'",
                "Queue timeout after 30s",
            ]),
            stack_trace=random.choice(STACK_TRACES),
            agent_name=run.agent_name,
            resolved=random.random() > 0.4,
            created_at=run.started_at,
        ))
    # Add some standalone errors
    for _ in range(30):
        errors.append(ErrorEvent(
            error_type=random.choice(ERROR_TYPES),
            severity=random.choice(SEVERITIES),
            title="Background Error",
            message="Unexpected error in background task",
            agent_name=random.choice(AGENTS),
            resolved=False,
            created_at=rand_dt(7),
        ))
    session.add_all(errors)
    session.commit()
    print(f"    ✓ {len(errors)} error events seeded")


def seed_queue_jobs(session, count=200):
    print(f"  → Seeding {count} queue jobs...")
    jobs = []
    for _ in range(count):
        status = random.choices(
            ["completed", "failed", "queued", "active", "dead_letter"],
            weights=[0.70, 0.12, 0.08, 0.05, 0.05]
        )[0]
        created = rand_dt(7)
        jobs.append(QueueJob(
            job_id=str(uuid.uuid4()),
            queue_name=random.choice(["default", "priority", "media"]),
            task_type=random.choice(["process_whatsapp_message", "process_image", "sync_products"]),
            status=status,
            priority=random.randint(1, 10),
            created_at=created,
            started_at=created + timedelta(seconds=random.uniform(0.1, 5)) if status != "queued" else None,
            completed_at=created + timedelta(seconds=random.uniform(1, 30)) if status in ("completed", "failed") else None,
            retry_count=random.randint(0, 3),
        ))
    session.add_all(jobs)
    session.commit()
    print(f"    ✓ {count} queue jobs seeded")


def seed_media(session, runs):
    print("  → Seeding media assets...")
    assets = []
    new_product_runs = [r for r in runs if r.task_type == "new_product"]
    for run in new_product_runs[:100]:
        for _ in range(random.randint(1, 3)):
            status = random.choices(
                ["completed", "failed", "processing"],
                weights=[0.80, 0.12, 0.08]
            )[0]
            assets.append(MediaAsset(
                workflow_run_id=run.id,
                filename=f"product_{uuid.uuid4().hex[:8]}.jpg",
                file_type=random.choice(["jpg", "png", "psd"]),
                file_size_bytes=random.randint(50000, 5000000),
                processing_status=status,
                storage_path=f"/processed_images/{uuid.uuid4().hex[:8]}.jpg",
                processing_duration_ms=random.randint(500, 8000) if status == "completed" else None,
                is_duplicate=random.random() < 0.08,
                image_hash=uuid.uuid4().hex,
                created_at=run.started_at,
            ))
    session.add_all(assets)
    session.commit()
    print(f"    ✓ {len(assets)} media assets seeded")


def seed_wc_ops(session, runs):
    print("  → Seeding WooCommerce operations...")
    ops = []
    for run in runs:
        if run.status in ("success", "failed"):
            for op_type in random.choices(WC_OPS, k=random.randint(1, 3)):
                ops.append(WooCommerceOp(
                    workflow_run_id=run.id,
                    operation_type=op_type,
                    product_id=random.randint(100, 9999),
                    product_name=random.choice(PRODUCT_NAMES),
                    status=random.choices(["success", "failed"], weights=[0.88, 0.12])[0],
                    api_latency_ms=random.randint(100, 3000),
                    created_at=run.started_at + timedelta(milliseconds=random.randint(500, 5000)),
                ))
    session.add_all(ops)
    session.commit()
    print(f"    ✓ {len(ops)} WooCommerce ops seeded")


def seed_logs(session, runs):
    print("  → Seeding system logs...")
    logs = []
    messages = {
        "INFO": [
            "Task started: process_whatsapp_message",
            "Product found in WooCommerce",
            "Stock status updated successfully",
            "Image processed through PSD template",
            "Product created in WooCommerce",
            "Confirmation sent to WhatsApp group",
        ],
        "WARN": [
            "Low confidence classification (62%)",
            "Fuzzy match below threshold, using best match",
            "Retry attempt 2 of 3",
            "Rate limit approaching OpenAI API",
        ],
        "ERROR": [
            "WooCommerce API request failed",
            "GPT response JSON parse error",
            "Image download timeout",
        ],
        "DEBUG": [
            "Encoding image as base64",
            "Sending request to OpenAI API",
            "WooCommerce response received",
        ],
    }
    for run in random.sample(runs, min(200, len(runs))):
        level = random.choice(LOG_LEVELS)
        logs.append(SystemLog(
            level=level,
            message=random.choice(messages.get(level, messages["INFO"])),
            workflow_run_id=run.id,
            agent_name=run.agent_name,
            created_at=run.started_at + timedelta(milliseconds=random.randint(0, 5000)),
        ))
    session.add_all(logs)
    session.commit()
    print(f"    ✓ {len(logs)} log entries seeded")


def seed_alerts(session):
    print("  → Seeding alerts...")
    alert_templates = [
        ("high_failure_rate", "critical", "High Failure Rate Detected", "Failure rate exceeded 20% in the last hour"),
        ("gpt_timeout", "warning", "GPT API Timeout", "OpenAI API responded slowly (>3s) for 5 consecutive requests"),
        ("queue_overload", "warning", "Queue Depth High", "Queue depth reached 45 jobs"),
        ("wc_downtime", "critical", "WooCommerce API Unreachable", "WooCommerce API returned 503 for 10 minutes"),
        ("high_ai_cost", "info", "Daily AI Cost Approaching Limit", "AI cost today: $8.42 (limit: $10.00)"),
        ("worker_crash", "critical", "Worker Process Crashed", "Background worker stopped unexpectedly"),
    ]
    alerts = []
    for alert_type, severity, title, message in alert_templates:
        alerts.append(Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            acknowledged=random.random() > 0.5,
            created_at=rand_dt(7),
        ))
    session.add_all(alerts)
    session.commit()
    print(f"    ✓ {len(alerts)} alerts seeded")


# ── Main ─────────────────────────────────────────────────────────────────────

def run_seed(database_url: str = None):
    print("\n🌱 Seeding NEXTGIC Dashboard database...\n")
    engine = init_dashboard_db(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        seed_users(session)
        seed_settings(session)
        runs = seed_workflows(session, count=500)
        seed_ai_requests(session, runs)
        seed_errors(session, runs)
        seed_queue_jobs(session, count=200)
        seed_media(session, runs)
        seed_wc_ops(session, runs)
        seed_logs(session, runs)
        seed_alerts(session)
        print("\n✅ Seed complete!\n")
        print("  Login: admin@nextgic.ai / admin123")
        print("  Login: operator@nextgic.ai / operator123")
        print("  Login: dev@nextgic.ai / dev123\n")
    finally:
        session.close()


if __name__ == "__main__":
    db_url = os.getenv("DASHBOARD_DATABASE_URL", "sqlite:///./nextgic_dashboard.db")
    run_seed(db_url)
