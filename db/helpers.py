"""
db/helpers.py
Convenience functions for logging jobs, deduplicating messages,
and caching product lookups.
"""

import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.database import JobLog, ProcessedMessage, ProductCache

PRODUCT_CACHE_TTL_MINUTES = 60


# ── Job Logging ────────────────────────────────────────────────────────────

def log_job(db: Session, task_type: str, status: str,
            result: dict = None, error: str = None,
            duration_sec: float = None, whatsapp_msg_id: str = None,
            input_text: str = None):
    """Write a job result to job_log table."""
    row = JobLog(
        task_type=task_type,
        status=status,
        duration_sec=duration_sec,
        whatsapp_msg_id=whatsapp_msg_id,
        input_text=input_text[:1000] if input_text else None,
        result_json=json.dumps(result) if result else None,
        error_msg=error,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    try:
        from ws.events import notify_task_created
        notify_task_created(row)
    except Exception:
        pass
    return row


def get_recent_jobs(db: Session, limit: int = 50) -> list:
    """Return the most recent job log entries."""
    return (
        db.query(JobLog)
        .order_by(JobLog.created_at.desc())
        .limit(limit)
        .all()
    )


# ── Message Deduplication ──────────────────────────────────────────────────

def is_already_processed(db: Session, message_id: str) -> bool:
    """Return True if this WhatsApp message ID was already handled."""
    return (
        db.query(ProcessedMessage)
        .filter(ProcessedMessage.message_id == message_id)
        .first()
    ) is not None


def mark_processed(db: Session, message_id: str,
                   task_type: str = None, success: bool = True):
    """Record that a WhatsApp message has been processed."""
    row = ProcessedMessage(
        message_id=message_id,
        task_type=task_type,
        success=success,
    )
    db.add(row)
    db.commit()


# ── Product Cache ──────────────────────────────────────────────────────────

def get_cached_product_id(db: Session, product_name: str) -> int | None:
    """
    Return cached WooCommerce product ID for a given name, if still fresh.
    Returns None if not cached or expired.
    """
    row = (
        db.query(ProductCache)
        .filter(ProductCache.product_name == product_name)
        .first()
    )
    if not row:
        return None

    age = datetime.utcnow() - row.cached_at
    if age > timedelta(minutes=PRODUCT_CACHE_TTL_MINUTES):
        db.delete(row)
        db.commit()
        return None

    return row.product_id


def cache_product(db: Session, product_name: str, product_id: int):
    """Store or update a product name → ID mapping in cache."""
    existing = (
        db.query(ProductCache)
        .filter(ProductCache.product_name == product_name)
        .first()
    )
    if existing:
        existing.product_id = product_id
        existing.cached_at  = datetime.utcnow()
    else:
        db.add(ProductCache(product_name=product_name, product_id=product_id))
    db.commit()
