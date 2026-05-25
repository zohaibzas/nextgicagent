"""Dashboard user model and helpers."""

import os
from datetime import datetime

import bcrypt
from sqlalchemy import Column, DateTime, Integer, String

from db.database import Base, SessionLocal, init_db


class DashboardUser(Base):
    __tablename__ = "dashboard_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(String(32), default="viewer", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_user(email: str, password: str, name: str | None = None, role: str = "viewer"):
    init_db()
    session = SessionLocal()
    try:
        existing = session.query(DashboardUser).filter(DashboardUser.email == email).first()
        if existing:
            raise ValueError(f"User {email} already exists")
        user = DashboardUser(
            email=email,
            password_hash=hash_password(password),
            name=name or email.split("@")[0],
            role=role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def ensure_default_admin():
    """Create a default admin in dev if no users exist."""
    init_db()
    session = SessionLocal()
    try:
        if session.query(DashboardUser).count() > 0:
            return
    finally:
        session.close()
    default_email = os.getenv("DASHBOARD_ADMIN_EMAIL", "admin@nextgic.com")
    default_password = os.getenv("DASHBOARD_ADMIN_PASSWORD", "nextgic")
    create_user(default_email, default_password, name="Admin", role="admin")
