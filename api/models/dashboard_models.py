"""
api/models/dashboard_models.py
Extended database models for the NEXTGIC AI OPERATIONS CENTER dashboard.
These tables are ADDITIVE — they do not modify the existing backend tables.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean,
    DateTime, Text, Float, BigInteger, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nextgic_dashboard.db")


class Base(DeclarativeBase):
    pass


def _uuid():
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Workflow Tracking
# ---------------------------------------------------------------------------

class WorkflowRun(Base):
    """One row per complete workflow execution triggered by a WhatsApp message."""
    __tablename__ = "workflow_runs"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    run_id          = Column(String(36), default=_uuid, unique=True, nullable=False, index=True)
    agent_name      = Column(String(64), nullable=False, index=True)   # intake | oos | duplicate | new_product
    task_type       = Column(String(64), nullable=True)
    status          = Column(String(32), nullable=False, default="running", index=True)
    # running | success | failed | retrying | queued | cancelled
    started_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at    = Column(DateTime, nullable=True)
    duration_ms     = Column(Integer, nullable=True)
    input_data      = Column(Text, nullable=True)   # JSON string
    output_data     = Column(Text, nullable=True)   # JSON string
    error_msg       = Column(Text, nullable=True)
    retry_count     = Column(Integer, default=0)
    parent_run_id   = Column(String(36), nullable=True)
    whatsapp_msg_id = Column(String(256), nullable=True, index=True)
    user_phone      = Column(String(64), nullable=True)
    wc_product_id   = Column(Integer, nullable=True, index=True)

    steps           = relationship("WorkflowStep", back_populates="workflow_run", cascade="all, delete-orphan")
    ai_requests     = relationship("AIRequest", back_populates="workflow_run", cascade="all, delete-orphan")
    error_events    = relationship("ErrorEvent", back_populates="workflow_run", cascade="all, delete-orphan")
    media_assets    = relationship("MediaAsset", back_populates="workflow_run", cascade="all, delete-orphan")
    wc_ops          = relationship("WooCommerceOp", back_populates="workflow_run", cascade="all, delete-orphan")


class WorkflowStep(Base):
    """Individual step within a workflow execution."""
    __tablename__ = "workflow_steps"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name       = Column(String(128), nullable=False)
    step_order      = Column(Integer, nullable=False)
    status          = Column(String(32), nullable=False, default="pending")
    started_at      = Column(DateTime, nullable=True)
    completed_at    = Column(DateTime, nullable=True)
    duration_ms     = Column(Integer, nullable=True)
    input_data      = Column(Text, nullable=True)
    output_data     = Column(Text, nullable=True)
    error_data      = Column(Text, nullable=True)
    step_type       = Column(String(64), nullable=True)
    # whatsapp_receive | image_download | gpt_classify | task_route |
    # wc_search | wc_update | wc_create | image_process | confirmation_send

    workflow_run    = relationship("WorkflowRun", back_populates="steps")


# ---------------------------------------------------------------------------
# AI Tracking
# ---------------------------------------------------------------------------

class AIRequest(Base):
    """Every GPT/NVIDIA API call made during a workflow."""
    __tablename__ = "ai_requests"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    model           = Column(String(128), nullable=False)
    prompt_text     = Column(Text, nullable=True)
    response_text   = Column(Text, nullable=True)
    prompt_tokens   = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens    = Column(Integer, nullable=True)
    cost_usd        = Column(Float, nullable=True)
    latency_ms      = Column(Integer, nullable=True)
    success         = Column(Boolean, default=True)
    error_msg       = Column(Text, nullable=True)
    request_type    = Column(String(64), nullable=True)  # classify | extract | vision
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    workflow_run    = relationship("WorkflowRun", back_populates="ai_requests")


# ---------------------------------------------------------------------------
# Error Tracking
# ---------------------------------------------------------------------------

class ErrorEvent(Base):
    """Every error thrown during workflow execution."""
    __tablename__ = "error_events"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    error_type      = Column(String(128), nullable=False, index=True)
    # gpt_failure | wc_api_error | queue_failure | image_failure |
    # auth_failure | validation_error | timeout | unknown
    severity        = Column(String(16), nullable=False, default="error", index=True)
    # critical | error | warning | info
    title           = Column(String(256), nullable=False)
    message         = Column(Text, nullable=True)
    stack_trace     = Column(Text, nullable=True)
    metadata_json   = Column(Text, nullable=True)
    agent_name      = Column(String(64), nullable=True, index=True)
    resolved        = Column(Boolean, default=False, index=True)
    resolved_at     = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    workflow_run    = relationship("WorkflowRun", back_populates="error_events")


# ---------------------------------------------------------------------------
# Queue Tracking
# ---------------------------------------------------------------------------

class QueueJob(Base):
    """Every job submitted to the task queue."""
    __tablename__ = "queue_jobs"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    job_id          = Column(String(36), default=_uuid, unique=True, nullable=False, index=True)
    queue_name      = Column(String(64), nullable=False, default="default", index=True)
    task_type       = Column(String(64), nullable=False)
    status          = Column(String(32), nullable=False, default="queued", index=True)
    # queued | active | completed | failed | retrying | dead_letter
    priority        = Column(Integer, default=5)
    payload         = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at      = Column(DateTime, nullable=True)
    completed_at    = Column(DateTime, nullable=True)
    retry_count     = Column(Integer, default=0)
    max_retries     = Column(Integer, default=3)
    error_json      = Column(Text, nullable=True)
    worker_id       = Column(String(64), nullable=True)


# ---------------------------------------------------------------------------
# Media Tracking
# ---------------------------------------------------------------------------

class MediaAsset(Base):
    """Every image or file processed through the media pipeline."""
    __tablename__ = "media_assets"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id     = Column(Integer, ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    filename            = Column(String(512), nullable=False)
    original_filename   = Column(String(512), nullable=True)
    file_type           = Column(String(32), nullable=True)  # jpg | png | psd | webp
    file_size_bytes     = Column(BigInteger, nullable=True)
    processing_status   = Column(String(32), nullable=False, default="pending", index=True)
    # pending | processing | completed | failed
    storage_path        = Column(Text, nullable=True)
    storage_url         = Column(Text, nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    error_msg           = Column(Text, nullable=True)
    is_duplicate        = Column(Boolean, default=False)
    image_hash          = Column(String(64), nullable=True, index=True)
    wc_attachment_id    = Column(Integer, nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    workflow_run        = relationship("WorkflowRun", back_populates="media_assets")


# ---------------------------------------------------------------------------
# WooCommerce Operations
# ---------------------------------------------------------------------------

class WooCommerceOp(Base):
    """Every WooCommerce API call made by an agent."""
    __tablename__ = "woocommerce_ops"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    operation_type  = Column(String(64), nullable=False, index=True)
    # product_create | product_update | product_search | product_duplicate |
    # stock_update | category_create | image_upload
    product_id      = Column(Integer, nullable=True, index=True)
    product_name    = Column(String(512), nullable=True)
    status          = Column(String(32), nullable=False, default="success", index=True)
    api_latency_ms  = Column(Integer, nullable=True)
    request_data    = Column(Text, nullable=True)
    response_data   = Column(Text, nullable=True)
    error_msg       = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    workflow_run    = relationship("WorkflowRun", back_populates="wc_ops")


# ---------------------------------------------------------------------------
# System Logs
# ---------------------------------------------------------------------------

class SystemLog(Base):
    """Structured log entries for the dashboard log viewer."""
    __tablename__ = "system_logs"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    level           = Column(String(16), nullable=False, default="INFO", index=True)
    # DEBUG | INFO | WARN | ERROR | CRITICAL
    message         = Column(Text, nullable=False)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_name      = Column(String(64), nullable=True, index=True)
    step_name       = Column(String(128), nullable=True)
    metadata_json   = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

class Alert(Base):
    """System-generated alerts for operational issues."""
    __tablename__ = "alerts"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    alert_type      = Column(String(64), nullable=False, index=True)
    # high_failure_rate | gpt_timeout | queue_overload | wc_downtime |
    # worker_crash | high_ai_cost | disk_usage
    severity        = Column(String(16), nullable=False, default="warning", index=True)
    # info | warning | critical
    title           = Column(String(256), nullable=False)
    message         = Column(Text, nullable=True)
    metadata_json   = Column(Text, nullable=True)
    acknowledged    = Column(Boolean, default=False, index=True)
    acknowledged_by = Column(Integer, ForeignKey("dashboard_users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Users (JWT Auth)
# ---------------------------------------------------------------------------

class DashboardUser(Base):
    """Dashboard users with role-based access."""
    __tablename__ = "dashboard_users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    email           = Column(String(256), unique=True, nullable=False, index=True)
    name            = Column(String(256), nullable=False)
    password_hash   = Column(String(256), nullable=False)
    role            = Column(String(32), nullable=False, default="viewer")
    # admin | operator | developer | viewer
    avatar_url      = Column(String(512), nullable=True)
    last_login      = Column(DateTime, nullable=True)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)


# ---------------------------------------------------------------------------
# Webhook Events
# ---------------------------------------------------------------------------

class WebhookEvent(Base):
    """Incoming webhook events (WhatsApp messages, etc.)."""
    __tablename__ = "webhook_events"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    source          = Column(String(64), nullable=False, default="whatsapp", index=True)
    event_type      = Column(String(128), nullable=False)
    payload         = Column(Text, nullable=True)
    processed       = Column(Boolean, default=False, index=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True)
    error_msg       = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class SystemSetting(Base):
    """Key-value store for system configuration."""
    __tablename__ = "system_settings"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    key         = Column(String(256), unique=True, nullable=False, index=True)
    value       = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_secret   = Column(Boolean, default=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------------------------------------------------------------------------
# Database Init
# ---------------------------------------------------------------------------

def get_engine(database_url: str = None):
    url = database_url or DATABASE_URL
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, echo=False, **kwargs)


def init_dashboard_db(database_url: str = None):
    """Create all dashboard tables. Safe to call on startup."""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine
