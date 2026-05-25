"""JWT create/verify for dashboard users."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

JWT_SECRET = os.getenv("JWT_SECRET", "nextgic-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))


def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
