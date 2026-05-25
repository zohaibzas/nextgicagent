"""
main.py
FastAPI backend — now with:
  - API key authentication
  - Structured logging
  - SQLite database (job logs, deduplication, product cache)
  - Queue abstraction (sync now, Celery-ready)
  - /logs endpoint to inspect recent jobs
  - /dashboard/* endpoints for the HTML Operations Dashboard

Run:
    uvicorn main:app --host 0.0.0.0 --port 8000

Manual test (no WhatsApp needed):
    python main.py <image_path> [text_message]
"""

import os, sys, shutil, time, re, json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import FastAPI, UploadFile, File, Form, Depends, Query, WebSocket, WebSocketDisconnect
from websockets_manager import manager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional

from logger import get_logger
from middleware.auth import APIKeyMiddleware
from auth.router import router as auth_router
from auth.models import ensure_default_admin
from db.database import init_db, get_db, SessionLocal, JobLog, ProcessedMessage, ProductCache
from db import helpers as db_helpers
from job_queue.worker import enqueue_task

log = get_logger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Log file path ──────────────────────────────────────────────────────────
LOG_DIR = os.getenv("LOG_DIR", "./logs")
AGENT_LOG_FILE = os.path.join(LOG_DIR, "agent.log")


# ── App lifecycle ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting Nextgic Agent API...")
    init_db()
    ensure_default_admin()
    log.info("Database initialised")
    yield
    log.info("Shutting down")

app = FastAPI(title="Nextgic Product Agent", version="2.0.0", lifespan=lifespan)

app.add_middleware(APIKeyMiddleware)

_cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()] or ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# ── WebSockets ─────────────────────────────────────────────────────────────

async def _websocket_live(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await _websocket_live(websocket)


@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await _websocket_live(websocket)



# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/process")
async def process_message(
    text: str = Form(default=""),
    msg_id: str = Form(default=""),
    images: List[UploadFile] = File(default=[]),
):
    """
    Receive WhatsApp message content, run appropriate agent, return result.
    Called by whatsapp/bot.js on every relevant group message.
    """
    saved_paths = []

    for img in images:
        filename = f"{int(time.time() * 1000)}_{img.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(img.file, f)
        saved_paths.append(filepath)
        log.info("Image saved: %s", filename)

    if not saved_paths:
        log.warning("/process called with no images")
        return JSONResponse({"success": False, "error": "No images provided"})

    log.info("Dispatching task | msg_id=%s | images=%d | text='%s'",
             msg_id or "?", len(saved_paths), text[:80])

    result = enqueue_task("process_whatsapp_message", {
        "image_paths":  saved_paths,
        "text_message": text,
        "msg_id":       msg_id or None,
    })

    # Cleanup temp files (synchronous mode only — Celery worker cleans its own)
    if not result.get("queued"):
        for p in saved_paths:
            try: os.remove(p)
            except Exception: pass

    return JSONResponse(result.get("result", result))


@app.get("/logs")
def get_logs(limit: int = 50):
    """Return recent job logs. Useful for debugging without SSH."""
    session = SessionLocal()
    try:
        jobs = db_helpers.get_recent_jobs(session, limit=limit)
        return [{
            "id":           j.id,
            "created_at":   j.created_at.isoformat(),
            "task_type":    j.task_type,
            "status":       j.status,
            "duration_sec": j.duration_sec,
            "message_id":   j.whatsapp_msg_id,
            "error":        j.error_msg,
        } for j in jobs]
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD API  — real data endpoints for nextgic_dashboard.html
# All routes bypass APIKeyMiddleware by being prefixed with /dashboard/
# (the middleware only blocks /process). All responses are JSON.
# ══════════════════════════════════════════════════════════════════════════════

AGENT_MAP = {
    "oos":         {"key": "oos",         "label": "OOS",         "icon": "ti-package-off"},
    "duplicate":   {"key": "duplicate",   "label": "Duplicate",   "icon": "ti-copy"},
    "new_product": {"key": "new_product", "label": "New product", "icon": "ti-plus"},
    "unknown":     {"key": "unknown",     "label": "Intake",      "icon": "ti-mail-forward"},
}


@app.get("/dashboard/jobs")
def dashboard_jobs(
    limit: int = Query(default=100, le=500),
    agent: str = Query(default="all"),
    status: str = Query(default="all"),
    date: Optional[str] = Query(default=None),
):
    """
    Return job_log rows for the activity feed.
    Filters: agent (task_type), status, date (YYYY-MM-DD).
    """
    session = SessionLocal()
    try:
        q = session.query(JobLog).order_by(JobLog.created_at.desc())

        if agent != "all":
            q = q.filter(JobLog.task_type == agent)
        if status != "all":
            q = q.filter(JobLog.status == status)
        if date:
            try:
                day = datetime.strptime(date, "%Y-%m-%d")
                q = q.filter(
                    JobLog.created_at >= day,
                    JobLog.created_at < day + timedelta(days=1)
                )
            except ValueError:
                pass

        jobs = q.limit(limit).all()

        rows = []
        for j in jobs:
            # Parse result_json to extract product name if available
            product = ""
            try:
                if j.result_json:
                    r = json.loads(j.result_json)
                    product = (
                        r.get("product_name") or
                        r.get("source_product") or
                        r.get("message", "").split("'")[1] if "'" in r.get("message", "") else ""
                    )
            except Exception:
                pass

            agent_info = AGENT_MAP.get(j.task_type, AGENT_MAP["unknown"])
            rows.append({
                "id":           j.id,
                "created_at":   j.created_at.isoformat() if j.created_at else None,
                "task_type":    j.task_type,
                "agent_key":    agent_info["key"],
                "agent_label":  agent_info["label"],
                "agent_icon":   agent_info["icon"],
                "status":       j.status,
                "duration_sec": j.duration_sec,
                "whatsapp_msg_id": j.whatsapp_msg_id,
                "product":      product,
                "error":        j.error_msg,
                "input_text":   j.input_text,
            })
        return rows
    finally:
        session.close()


@app.get("/dashboard/kpis")
def dashboard_kpis(date: Optional[str] = Query(default=None)):
    """Return aggregated KPI metrics from job_log, processed_message, product_cache."""
    session = SessionLocal()
    try:
        q = session.query(JobLog)
        if date:
            try:
                day = datetime.strptime(date, "%Y-%m-%d")
                q = q.filter(
                    JobLog.created_at >= day,
                    JobLog.created_at < day + timedelta(days=1)
                )
            except ValueError:
                pass

        jobs = q.all()
        total   = len(jobs)
        success = sum(1 for j in jobs if j.status == "success")
        failed  = sum(1 for j in jobs if j.status == "failed")
        skipped = sum(1 for j in jobs if j.status == "skipped")
        durations = [j.duration_sec for j in jobs if j.duration_sec is not None]
        avg_dur = round(sum(durations) / len(durations), 2) if durations else 0

        dedup_count = session.query(ProcessedMessage).count()
        cache_count = session.query(ProductCache).count()

        # ── Extended KPIs ──────────────────────────────────────────────
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = sum(
            1 for j in jobs
            if j.created_at and j.created_at >= today_start
        )
        oos_count    = sum(1 for j in jobs if j.task_type == "oos")
        new_products = sum(1 for j in jobs if j.task_type == "new_product")
        error_rate   = round(failed / total * 100, 1) if total else 0.0
        wc_errors    = sum(
            1 for j in jobs
            if j.error_msg and ("woocommerce" in j.error_msg.lower() or "wc" in j.error_msg.lower())
        )

        return {
            "total_tasks":      total,
            "success":          success,
            "failed":           failed,
            "skipped":          skipped,
            "success_rate":     round(success / total * 100) if total else 0,
            "avg_duration":     avg_dur,
            "dedup_blocked":    dedup_count,
            "cache_hits":       cache_count,
            "wa_messages":      total,
            "open_errors":      failed,
            # Extended fields
            "today":            today_count,
            "oos_count":        oos_count,
            "new_products":     new_products,
            "ai_calls":         total,
            "ai_avg_duration":  avg_dur,
            "ai_error_rate":    error_rate,
            "wc_errors":        wc_errors,
            "images_processed": total,
        }
    finally:
        session.close()


@app.get("/dashboard/agents")
def dashboard_agents(date: Optional[str] = Query(default=None)):
    """Return per-agent health metrics derived from job_log."""
    session = SessionLocal()
    try:
        q = session.query(JobLog)
        if date:
            try:
                day = datetime.strptime(date, "%Y-%m-%d")
                q = q.filter(
                    JobLog.created_at >= day,
                    JobLog.created_at < day + timedelta(days=1)
                )
            except ValueError:
                pass
        jobs = q.all()

        result = []
        for key, info in AGENT_MAP.items():
            aj = [j for j in jobs if j.task_type == key]
            total = len(aj)
            success = sum(1 for j in aj if j.status == "success")
            failed  = sum(1 for j in aj if j.status == "failed")
            durations = [j.duration_sec for j in aj if j.duration_sec is not None]
            avg_dur = round(sum(durations) / len(durations), 2) if durations else 0
            sr = round(success / total * 100) if total else 0
            last_job = max((j.created_at for j in aj), default=None)

            result.append({
                "key":          key,
                "label":        info["label"],
                "icon":         info["icon"],
                "total":        total,
                "success":      success,
                "failed":       failed,
                "success_rate": sr,
                "avg_duration": avg_dur,
                "health":       "green" if sr >= 80 else ("amber" if sr >= 60 else "red"),
                "last_active":  last_job.isoformat() if last_job else None,
            })
        return result
    finally:
        session.close()


@app.get("/dashboard/errors")
def dashboard_errors(
    limit: int = Query(default=20, le=100),
    date: Optional[str] = Query(default=None),
):
    """Return failed job_log rows as error events."""
    session = SessionLocal()
    try:
        q = session.query(JobLog).filter(JobLog.error_msg.isnot(None))
        if date:
            try:
                day = datetime.strptime(date, "%Y-%m-%d")
                q = q.filter(
                    JobLog.created_at >= day,
                    JobLog.created_at < day + timedelta(days=1)
                )
            except ValueError:
                pass
        errors = q.order_by(JobLog.created_at.desc()).limit(limit).all()

        return [{
            "id":           e.id,
            "created_at":   e.created_at.isoformat() if e.created_at else None,
            "task_type":    e.task_type,
            "agent_label":  AGENT_MAP.get(e.task_type, AGENT_MAP["unknown"])["label"],
            "status":       e.status,
            "error_msg":    e.error_msg,
            "whatsapp_msg_id": e.whatsapp_msg_id,
            "duration_sec": e.duration_sec,
            "input_text":   e.input_text,
        } for e in errors]
    finally:
        session.close()


@app.get("/dashboard/db")
def dashboard_db():
    """Return raw DB stats: table row counts, dedup log, product cache."""
    session = SessionLocal()
    try:
        jobs = session.query(JobLog).order_by(JobLog.created_at.desc()).all()
        processed = session.query(ProcessedMessage).order_by(ProcessedMessage.processed_at.desc()).limit(20).all()
        cache = session.query(ProductCache).order_by(ProductCache.cached_at.desc()).all()
        now = datetime.utcnow()

        return {
            "stats": {
                "total":   len(jobs),
                "success": sum(1 for j in jobs if j.status == "success"),
                "failed":  sum(1 for j in jobs if j.status == "failed"),
                "skipped": sum(1 for j in jobs if j.status == "skipped"),
                "processed_message_rows": session.query(ProcessedMessage).count(),
                "product_cache_rows":     session.query(ProductCache).count(),
            },
            "dedup_log": [{
                "message_id":   p.message_id,
                "processed_at": p.processed_at.isoformat() if p.processed_at else None,
                "task_type":    p.task_type,
                "success":      p.success,
            } for p in processed],
            "product_cache": [{
                "product_name": c.product_name,
                "product_id":   c.product_id,
                "cached_at":    c.cached_at.isoformat() if c.cached_at else None,
                "ttl_minutes_left": max(0, round(60 - (now - c.cached_at).total_seconds() / 60)) if c.cached_at else 0,
            } for c in cache],
        }
    finally:
        session.close()


@app.get("/dashboard/charts")
def dashboard_charts(date: Optional[str] = Query(default=None)):
    """Return chart data: tasks per agent, hourly success rate."""
    session = SessionLocal()
    try:
        q = session.query(JobLog)
        if date:
            try:
                day = datetime.strptime(date, "%Y-%m-%d")
                q = q.filter(
                    JobLog.created_at >= day,
                    JobLog.created_at < day + timedelta(days=1)
                )
            except ValueError:
                pass
        jobs = q.all()

        # Tasks per agent
        agent_counts = defaultdict(int)
        for j in jobs:
            label = AGENT_MAP.get(j.task_type, AGENT_MAP["unknown"])["label"]
            agent_counts[label] += 1

        # Hourly success rate (last 12 hours)
        hourly = defaultdict(lambda: {"total": 0, "success": 0})
        cutoff = datetime.utcnow() - timedelta(hours=12)
        for j in jobs:
            if j.created_at and j.created_at >= cutoff:
                h = j.created_at.strftime("%H:00")
                hourly[h]["total"] += 1
                if j.status == "success":
                    hourly[h]["success"] += 1

        # Sort hours
        sorted_hours = sorted(hourly.keys())
        hourly_rates = []
        for h in sorted_hours:
            t = hourly[h]["total"]
            s = hourly[h]["success"]
            hourly_rates.append({
                "hour":  h,
                "rate":  round(s / t * 100) if t else 0,
                "total": t,
            })

        return {
            "tasks_by_agent": [
                {"label": k, "count": v} for k, v in agent_counts.items()
            ],
            "hourly_success": hourly_rates,
        }
    finally:
        session.close()


@app.get("/dashboard/logs")
def dashboard_logs_file(
    limit: int = Query(default=200, le=1000),
    level: Optional[str] = Query(default=None),
    agent: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    """
    Parse the rotating agent.log file and return structured log entries.
    Format: 2026-05-22 14:35:02 | INFO     | agents.oos_agent          | Message here
    """
    entries = []
    log_path = AGENT_LOG_FILE

    if not os.path.exists(log_path):
        # If no log file yet, return recent job_log entries as pseudo-logs
        session = SessionLocal()
        try:
            jobs = session.query(JobLog).order_by(JobLog.created_at.desc()).limit(50).all()
            for j in jobs:
                lv = "ERROR" if j.status == "failed" else "INFO"
                agent_label = AGENT_MAP.get(j.task_type, AGENT_MAP["unknown"])["label"]
                msg = j.error_msg if j.error_msg else f"Task {j.task_type} — {j.status}"
                if j.duration_sec:
                    msg += f" ({j.duration_sec}s)"
                entries.append({
                    "level":      lv,
                    "time":       j.created_at.strftime("%H:%M:%S") if j.created_at else "",
                    "full_time":  j.created_at.isoformat() if j.created_at else "",
                    "agent":      agent_label,
                    "module":     f"agents.{j.task_type}_agent",
                    "msg":        msg,
                })
        finally:
            session.close()
    else:
        # Parse actual log file
        log_pattern = re.compile(
            r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+)\s*\| ([^|]+)\| (.+)$"
        )
        agent_pattern = re.compile(r"agents\.(\w+)|queue\.(\w+)|tools\.(\w+)")

        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in reversed(lines):
                line = line.strip()
                m = log_pattern.match(line)
                if not m:
                    continue
                dt_str, lv, module, msg = m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()

                # Determine agent from module name
                am = agent_pattern.search(module)
                if am:
                    mod_name = am.group(1) or am.group(2) or am.group(3)
                    agent_lbl = AGENT_MAP.get(mod_name, {}).get("label", mod_name.replace("_", " ").title())
                else:
                    agent_lbl = module.split(".")[-1].title()

                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    time_str = dt.strftime("%H:%M:%S")
                    full_time = dt.isoformat()
                except ValueError:
                    time_str = dt_str[-8:]
                    full_time = dt_str

                entries.append({
                    "level":     lv,
                    "time":      time_str,
                    "full_time": full_time,
                    "agent":     agent_lbl,
                    "module":    module,
                    "msg":       msg,
                })

                if len(entries) >= limit * 3:  # pre-filter buffer
                    break
        except OSError:
            pass

    # Apply filters
    if level and level != "All levels":
        entries = [e for e in entries if e["level"] == level]
    if agent and agent.strip():
        entries = [e for e in entries if agent.lower() in e["agent"].lower()]
    if search:
        s = search.lower()
        entries = [e for e in entries if s in e["msg"].lower() or s in e["agent"].lower()]

    return entries[:limit]


# ══════════════════════════════════════════════════════════════════════════════
# REST API  — /api/* aliases for Next.js dashboard (spec Section 5)
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/api/kpis")
def api_kpis(date: Optional[str] = Query(default=None)):
    data = dashboard_kpis(date=date)
    return {
        "total": data["total_tasks"],
        "today": data["today"],
        "success_rate": data["success_rate"],
        "failed": data["failed"],
        "total_tasks": data["total_tasks"],
        "success": data["success"],
        "skipped": data["skipped"],
        "avg_duration": data["avg_duration"],
        "open_errors": data["open_errors"],
        "oos_count": data["oos_count"],
        "new_products": data["new_products"],
        "ai_calls": data["ai_calls"],
        "ai_avg_duration": data["ai_avg_duration"],
        "ai_error_rate": data["ai_error_rate"],
        "wc_errors": data["wc_errors"],
        "images_processed": data["images_processed"],
        "wa_messages": data["wa_messages"],
        "dedup_blocked": data["dedup_blocked"],
        "cache_hits": data["cache_hits"],
    }


@app.get("/api/tasks")
def api_tasks(
    limit: int = Query(default=100, le=500),
    agent: str = Query(default="all"),
    status: str = Query(default="all"),
    date: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    rows = dashboard_jobs(limit=limit, agent=agent, status=status, date=date)
    if search:
        s = search.lower()
        rows = [
            r for r in rows
            if s in (r.get("product") or "").lower()
            or s in (r.get("input_text") or "").lower()
            or s in f"wf_{r.get('id', 0):05d}"
        ]
    return [
        {**r, "workflow_id": f"wf_{r['id']:05d}"}
        for r in rows
    ]


@app.get("/api/tasks/{task_id}")
def api_task_detail(task_id: int):
    return api_workflow_detail(task_id)


@app.get("/api/agents")
def api_agents(date: Optional[str] = Query(default=None)):
    return dashboard_agents(date=date)


@app.get("/api/errors")
def api_errors(
    limit: int = Query(default=50, le=100),
    date: Optional[str] = Query(default=None),
):
    return dashboard_errors(limit=limit, date=date)


@app.get("/api/logs")
def api_logs(
    limit: int = Query(default=200, le=1000),
    level: Optional[str] = Query(default=None),
    agent: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    return dashboard_logs_file(limit=limit, level=level, agent=agent, search=search)


@app.get("/api/workflows/{workflow_id}")
def api_workflow_detail(workflow_id: int):
    session = SessionLocal()
    try:
        job = session.query(JobLog).filter(JobLog.id == workflow_id).first()
        if not job:
            return JSONResponse({"error": "Workflow not found"}, status_code=404)
        steps = []
        if job.created_at:
            steps.append({
                "step_name": "intake",
                "status": "success",
                "started_at": job.created_at.isoformat(),
                "duration_ms": int((job.duration_sec or 0) * 500),
            })
        steps.append({
            "step_name": job.task_type or "classify",
            "status": job.status,
            "started_at": job.created_at.isoformat() if job.created_at else None,
            "duration_ms": int((job.duration_sec or 0) * 1000),
            "error_msg": job.error_msg,
        })
        result = None
        try:
            if job.result_json:
                result = json.loads(job.result_json)
        except Exception:
            pass
        agent_info = AGENT_MAP.get(job.task_type, AGENT_MAP["unknown"])
        product = ""
        if result:
            product = result.get("product_name") or result.get("source_product") or ""
        return {
            "id": job.id,
            "workflow_id": f"wf_{job.id:05d}",
            "agent_label": agent_info["label"],
            "task_type": job.task_type,
            "status": job.status,
            "duration_sec": job.duration_sec,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "product": product,
            "error": job.error_msg,
            "input_text": job.input_text,
            "whatsapp_msg_id": job.whatsapp_msg_id,
            "steps": steps,
            "ai_request": job.input_text,
            "ai_response": result,
            "woocommerce": result,
        }
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS  — analytics, retry, resolve
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/api/analytics")
def api_analytics():
    """Return 30-day chart data for the Analytics page."""
    session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        jobs = (
            session.query(JobLog)
            .filter(JobLog.created_at >= cutoff)
            .order_by(JobLog.created_at.asc())
            .all()
        )

        # ── Bucket jobs by date string ─────────────────────────────────
        by_date = defaultdict(list)
        for j in jobs:
            if j.created_at:
                day_key = j.created_at.strftime("%Y-%m-%d")
                by_date[day_key].append(j)

        sorted_dates = sorted(by_date.keys())
        num_days = len(sorted_dates) or 1

        # 1. task_volume
        task_volume = [
            {"date": d, "count": len(by_date[d])} for d in sorted_dates
        ]

        # 2. success_vs_failed
        success_vs_failed = []
        for d in sorted_dates:
            s = sum(1 for j in by_date[d] if j.status == "success")
            f = sum(1 for j in by_date[d] if j.status == "failed")
            success_vs_failed.append({"date": d, "success": s, "failed": f})

        # 3. tasks_by_agent
        agent_counts = defaultdict(int)
        for j in jobs:
            label = AGENT_MAP.get(j.task_type, AGENT_MAP["unknown"])["label"]
            agent_counts[label] += 1
        tasks_by_agent = [
            {"agent": k, "count": v} for k, v in agent_counts.items()
        ]

        # 4. avg_duration_trend
        avg_duration_trend = []
        for d in sorted_dates:
            durs = [j.duration_sec for j in by_date[d] if j.duration_sec is not None]
            avg_s = round(sum(durs) / len(durs), 2) if durs else 0
            avg_duration_trend.append({"date": d, "avg_sec": avg_s})

        # 5. error_rate_trend
        error_rate_trend = []
        for d in sorted_dates:
            t = len(by_date[d])
            f = sum(1 for j in by_date[d] if j.status == "failed")
            error_rate_trend.append({"date": d, "rate": round(f / t * 100, 1) if t else 0})

        # 6. tasks_by_hour (average count per hour across the 30 days)
        hour_totals = defaultdict(int)
        for j in jobs:
            if j.created_at:
                hour_totals[j.created_at.hour] += 1
        tasks_by_hour = [
            {"hour": h, "avg_count": round(hour_totals[h] / num_days, 2)}
            for h in range(24)
        ]

        # 7. task_type_split (raw task_type key, not label)
        type_counts = defaultdict(int)
        for j in jobs:
            type_counts[j.task_type] += 1
        task_type_split = [
            {"type": k, "count": v} for k, v in type_counts.items()
        ]

        return {
            "task_volume":        task_volume,
            "success_vs_failed":  success_vs_failed,
            "tasks_by_agent":     tasks_by_agent,
            "avg_duration_trend": avg_duration_trend,
            "error_rate_trend":   error_rate_trend,
            "tasks_by_hour":      tasks_by_hour,
            "task_type_split":    task_type_split,
        }
    finally:
        session.close()


@app.post("/api/tasks/{task_id}/retry")
def api_retry_task(task_id: int):
    """Re-queue a failed task by creating a new JobLog entry with status='pending'."""
    session = SessionLocal()
    try:
        job = session.query(JobLog).filter(JobLog.id == task_id).first()
        if not job:
            return JSONResponse({"success": False, "error": "Task not found"}, status_code=404)
        if job.status != "failed":
            return JSONResponse(
                {"success": False, "error": f"Task is '{job.status}', only failed tasks can be retried"},
                status_code=400,
            )

        new_job = JobLog(
            task_type=job.task_type,
            status="pending",
            input_text=job.input_text,
            whatsapp_msg_id=job.whatsapp_msg_id,
        )
        session.add(new_job)
        session.commit()
        session.refresh(new_job)

        return {
            "success": True,
            "new_task": {
                "id":         new_job.id,
                "created_at": new_job.created_at.isoformat() if new_job.created_at else None,
                "task_type":  new_job.task_type,
                "status":     new_job.status,
                "input_text": new_job.input_text,
            },
        }
    finally:
        session.close()


@app.patch("/api/errors/{error_id}/resolve")
def api_resolve_error(error_id: int):
    """Mark an errored JobLog row as resolved."""
    session = SessionLocal()
    try:
        job = session.query(JobLog).filter(JobLog.id == error_id).first()
        if not job:
            return JSONResponse({"success": False, "error": "Task not found"}, status_code=404)
        if not job.error_msg:
            return JSONResponse(
                {"success": False, "error": "Task has no error to resolve"},
                status_code=400,
            )

        job.status = "resolved"
        session.commit()

        return {
            "success": True,
            "id":      job.id,
            "status":  job.status,
        }
    finally:
        session.close()


# ── Manual CLI test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py <image_path> [text_message]")
        print("  uvicorn main:app --port 8000")
        sys.exit(1)

    init_db()

    image_path   = sys.argv[1]
    text_message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    log.info("Manual test: image=%s text='%s'", image_path, text_message)

    result = enqueue_task("process_whatsapp_message", {
        "image_paths":  [image_path],
        "text_message": text_message,
        "msg_id":       None,
    })

    import json
    final = result.get("result", result)
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(json.dumps(final, indent=2))
