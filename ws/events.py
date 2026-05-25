"""Emit WebSocket events when jobs are logged (sync-safe)."""

import asyncio
import json
from typing import Any, Dict

from websockets_manager import manager

AGENT_MAP = {
    "oos": {"key": "oos", "label": "OOS"},
    "duplicate": {"key": "duplicate", "label": "Duplicate"},
    "new_product": {"key": "new_product", "label": "New product"},
    "unknown": {"key": "unknown", "label": "Intake"},
}


def _job_to_task_payload(row) -> Dict[str, Any]:
    product = ""
    try:
        if row.result_json:
            r = json.loads(row.result_json)
            product = (
                r.get("product_name")
                or r.get("source_product")
                or ""
            )
    except Exception:
        pass
    agent_info = AGENT_MAP.get(row.task_type, AGENT_MAP["unknown"])
    return {
        "id": row.id,
        "workflow_id": f"wf_{row.id:05d}",
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "task_type": row.task_type,
        "agent_key": agent_info["key"],
        "agent_label": agent_info["label"],
        "status": row.status,
        "duration_sec": row.duration_sec,
        "whatsapp_msg_id": row.whatsapp_msg_id,
        "product": product,
        "error": row.error_msg,
        "input_text": row.input_text,
    }


def notify_task_created(row):
    """Broadcast new task to connected dashboard clients."""
    event_type = "task.created"
    if row.status == "failed":
        event_type = "workflow.failed"
    elif row.status == "success":
        event_type = "workflow.completed"
    elif row.status == "pending":
        event_type = "workflow.started"

    payload = _job_to_task_payload(row)

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(event_type, payload))
    except RuntimeError:
        pass
