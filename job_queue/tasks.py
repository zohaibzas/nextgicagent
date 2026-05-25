"""
job_queue/tasks.py
Task definitions. Each task calls the appropriate agent.
When Celery is active, these become @celery_app.task decorated functions.
"""

import time
import json
from logger import get_logger
from db.database import SessionLocal
from db import helpers as db

log = get_logger(__name__)


def run_task(task_name: str, kwargs: dict) -> dict:
    """Synchronous task runner — called when QUEUE_BACKEND=sync."""
    if task_name == "process_whatsapp_message":
        return _process_whatsapp_message(**kwargs)
    else:
        return {"success": False, "error": f"Unknown task: {task_name}"}


def _process_whatsapp_message(
    image_paths: list,
    text_message: str = "",
    msg_id: str = None,
) -> dict:
    """
    Core task: classify and process a WhatsApp message through agents.
    Handles DB logging and deduplication.
    """
    from agents import intake_agent

    session = SessionLocal()
    start   = time.time()

    try:
        # Deduplication check
        if msg_id and db.is_already_processed(session, msg_id):
            log.info("Message %s already processed — skipping", msg_id)
            return {"success": True, "skipped": True, "reason": "already processed"}

        log.info("Processing message %s | images=%d text='%s'",
                 msg_id or "?", len(image_paths), text_message[:80])

        # Run agents
        result = intake_agent.run(
            image_paths=image_paths,
            text_message=text_message,
        )

        duration = round(time.time() - start, 2)
        status   = "success" if result.get("success") else "failed"

        # Log to DB
        db.log_job(
            db=session,
            task_type=result.get("task", "unknown"),
            status=status,
            result=result,
            error=result.get("error"),
            duration_sec=duration,
            whatsapp_msg_id=msg_id,
            input_text=text_message,
        )

        # Mark message as processed
        if msg_id:
            db.mark_processed(
                session, msg_id,
                task_type=result.get("task"),
                success=result.get("success", False),
            )

        log.info("Task done in %.2fs — %s: %s",
                 duration, status, result.get("message") or result.get("error"))

        return result

    except Exception as e:
        duration = round(time.time() - start, 2)
        log.exception("Task failed after %.2fs: %s", duration, e)

        db.log_job(
            db=session,
            task_type="unknown",
            status="failed",
            error=str(e),
            duration_sec=duration,
            whatsapp_msg_id=msg_id,
            input_text=text_message,
        )

        if msg_id:
            db.mark_processed(session, msg_id, success=False)

        return {"success": False, "error": str(e)}

    finally:
        session.close()
