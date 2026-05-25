"""
logger.py
Centralised logging for all agents and tools.
Writes to console + rotating file logs/agent.log

Usage:
    from logger import get_logger
    log = get_logger(__name__)
    log.info("Product found: %s", product_name)
    log.error("WooCommerce error: %s", err)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR   = os.getenv("LOG_DIR", "./logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

os.makedirs(LOG_DIR, exist_ok=True)

# ── Formatter ──────────────────────────────────────────────────────────────
_fmt = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── Handlers ───────────────────────────────────────────────────────────────
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_fmt)

_file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "agent.log"),
    maxBytes=5 * 1024 * 1024,   # 5 MB per file
    backupCount=5,               # keep last 5 rotated files
    encoding="utf-8",
)
_file_handler.setFormatter(_fmt)

# Separate file just for errors
_error_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "errors.log"),
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)
_error_handler.setLevel(logging.ERROR)
_error_handler.setFormatter(_fmt)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name.
    All loggers share the same handlers — one log file for the whole system.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(_console_handler)
        logger.addHandler(_file_handler)
        logger.addHandler(_error_handler)
        logger.propagate = False

    return logger
