"""
db/database.py
SQLite now. Switch to PostgreSQL by changing DATABASE_URL in .env.

Tables:
  - job_log       : every task attempted (success/fail, timing, payload)
  - processed_msg : WhatsApp message IDs already handled (deduplication)
  - product_cache : recently seen WooCommerce products (avoid redundant API calls)
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean,
    DateTime, Text, Float, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ── Connection ─────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./nextgic_agent.db"   # drop-in swap: postgresql+psycopg2://user:pass@host/db
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


# ── Models ─────────────────────────────────────────────────────────────────

class JobLog(Base):
    """One row per task attempted by any agent."""
    __tablename__ = "job_log"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    task_type     = Column(String(32), nullable=False)   # oos | duplicate | new_product | unknown
    status        = Column(String(16), nullable=False)   # success | failed | skipped
    duration_sec  = Column(Float, nullable=True)
    whatsapp_msg_id = Column(String(128), nullable=True)
    input_text    = Column(Text, nullable=True)
    result_json   = Column(Text, nullable=True)          # JSON string of agent result
    error_msg     = Column(Text, nullable=True)


class ProcessedMessage(Base):
    """Tracks WhatsApp message IDs we already handled — prevents double processing."""
    __tablename__ = "processed_message"
    __table_args__ = (UniqueConstraint("message_id", name="uq_message_id"),)

    id          = Column(Integer, primary_key=True, autoincrement=True)
    message_id  = Column(String(256), nullable=False, unique=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    task_type   = Column(String(32), nullable=True)
    success     = Column(Boolean, default=True)


class ProductCache(Base):
    """
    Short-lived cache of WooCommerce product name → ID mappings.
    Reduces redundant search API calls for frequently referenced products.
    TTL enforced in application logic (default 1 hour).
    """
    __tablename__ = "product_cache"
    __table_args__ = (UniqueConstraint("product_name", name="uq_product_name"),)

    id           = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(512), nullable=False, unique=True)
    product_id   = Column(Integer, nullable=False)
    cached_at    = Column(DateTime, default=datetime.utcnow)


# ── Init ───────────────────────────────────────────────────────────────────

def init_db():
    """Create all tables if they don't exist. Safe to call on every startup."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """FastAPI dependency — yields a DB session, closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
