"""
middleware/auth.py
API key authentication for all FastAPI routes.

How it works:
- Every request must include header:  X-API-Key: your_secret_key
- Key is set in .env as AGENT_API_KEY
- Requests without a valid key get 401 Unauthorized

Setup:
  Add to .env:
    AGENT_API_KEY=generate_a_long_random_string_here

Generate a key:
  python -c "import secrets; print(secrets.token_hex(32))"
"""

import os
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from logger import get_logger

log = get_logger(__name__)

AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")

# Routes that don't require auth (health check + dashboard UI)
PUBLIC_ROUTES = {"/health", "/", "/logs", "/docs", "/openapi.json", "/redoc"}
PUBLIC_PREFIXES = (
    "/dashboard/",
    "/dashboard",
    "/api/",
    "/auth/",
    "/ws",
)


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow all OPTIONS requests for CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # Always allow public routes and dashboard routes
        path = request.url.path
        if path in PUBLIC_ROUTES or path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)

        # Check for API key header
        api_key = request.headers.get("X-API-Key", "")

        if not AGENT_API_KEY:
            # No key configured — warn loudly but allow through (dev mode)
            log.warning("AGENT_API_KEY not set — running WITHOUT authentication. Set it in .env.")
            return await call_next(request)

        if api_key != AGENT_API_KEY:
            log.warning(
                "Unauthorized request to %s from %s",
                request.url.path,
                request.client.host if request.client else "unknown",
            )
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized. Provide a valid X-API-Key header."},
            )

        return await call_next(request)
