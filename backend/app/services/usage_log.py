"""Anonymous usage log for TiDB Cloud.

The log records what was asked and answered so the service can be improved.
It is deliberately anonymous: the browser session id is stored only as a
salted SHA-256 hash, and no API key, credential, IP address, or personal data
is ever written to the database.

A database problem must never break the answer flow, so every failure here is
logged server-side and swallowed.
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import time
from typing import Any

from app.config import get_settings
from app.db.models import QuestionLog
from app.db.session import get_session_factory

logger = logging.getLogger(__name__)

# Used only when SESSION_HASH_SALT is not configured. A random per-process salt
# still prevents a raw session id from ever being stored, it only means the
# hashes cannot be compared across restarts.
_fallback_salt = secrets.token_hex(16)


def _salt() -> str:
    configured = get_settings().session_hash_salt.strip()
    if configured:
        return configured
    return _fallback_salt


def hash_session_id(raw: str | None) -> str:
    """Return the salted hash of a browser session id.

    An empty or missing session id still produces a stable placeholder hash, so
    every row has a valid ``session_hash``.
    """
    value = (raw or "").strip()
    if not value:
        value = "anonymous"
    digest = hashlib.sha256(f"{_salt()}:{value}".encode("utf-8")).hexdigest()
    return digest[:64]


def log_question(
    *,
    question: str,
    answer: str,
    language: str,
    category: str | None,
    status: str,
    model_id: str,
    session_id: str | None,
    usage: Any = None,
    latency_ms: int | None = None,
    image_count: int = 0,
    location_count: int = 0,
    source_count: int = 0,
) -> None:
    """Write one question/answer exchange to the log.

    Does nothing when the database is not configured, and never raises.
    """
    settings = get_settings()
    if not settings.has_database_config:
        return

    usage = usage if usage is not None else None
    prompt_tokens = getattr(usage, "prompt_tokens", None)
    output_tokens = getattr(usage, "output_tokens", None)
    total_tokens = getattr(usage, "total_tokens", None)

    record = QuestionLog(
        session_hash=hash_session_id(session_id),
        question=question,
        answer=answer,
        language=language,
        category=category,
        status=status,
        model_id=model_id,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        image_count=image_count,
        location_count=location_count,
        source_count=source_count,
    )

    try:
        factory = get_session_factory()
        db = factory()
        try:
            db.add(record)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Usage log write failed: %s", exc)


def elapsed_ms(started_at: float) -> int:
    """Milliseconds since ``started_at`` (a ``time.monotonic()`` reading)."""
    return int((time.monotonic() - started_at) * 1000)


__all__ = ["elapsed_ms", "hash_session_id", "log_question"]
