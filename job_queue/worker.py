"""
job_queue/worker.py
Task queue abstraction layer.

NOW:    Synchronous execution (runs inline, no queue)
LATER:  Switch to Celery + Redis by setting QUEUE_BACKEND=celery in .env
        and running: celery -A job_queue.worker worker --loglevel=info

To activate Celery later:
  1. pip install celery redis
  2. Set in .env:
       QUEUE_BACKEND=celery
       REDIS_URL=redis://localhost:6379/0
  3. Start Redis: docker run -d -p 6379:6379 redis:alpine
  4. Start worker: celery -A job_queue.worker worker --loglevel=info
"""

import os
from logger import get_logger

log = get_logger(__name__)

QUEUE_BACKEND = os.getenv("QUEUE_BACKEND", "sync")   # "sync" | "celery"


# ── Celery setup (only loaded when backend=celery) ─────────────────────────

def _make_celery_app():
    try:
        from celery import Celery
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        app = Celery("nextgic", broker=redis_url, backend=redis_url)
        app.conf.update(
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],
            task_track_started=True,
        )
        return app
    except ImportError:
        log.warning("Celery not installed. pip install celery redis to enable.")
        return None


celery_app = _make_celery_app() if QUEUE_BACKEND == "celery" else None


# ── Public interface ───────────────────────────────────────────────────────

def enqueue_task(task_name: str, kwargs: dict) -> dict:
    """
    Submit a task to the queue (or run synchronously).
    Returns immediately with a job reference.

    task_name: "process_whatsapp_message"
    kwargs:    {"image_paths": [...], "text_message": "...", "msg_id": "..."}
    """
    if QUEUE_BACKEND == "celery" and celery_app:
        result = celery_app.send_task(
            f"job_queue.worker.{task_name}",
            kwargs=kwargs,
        )
        log.info("Task enqueued: %s (id=%s)", task_name, result.id)
        return {"queued": True, "task_id": result.id}
    else:
        # Synchronous fallback — run inline
        log.info("Running task synchronously: %s", task_name)
        from job_queue.tasks import run_task
        result = run_task(task_name, kwargs)
        return {"queued": False, "result": result}
