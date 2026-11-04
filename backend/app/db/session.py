"""SQLAlchemy engine/session wiring for TiDB Cloud.

The engine is created lazily and every call is wrapped so that a database
problem never breaks the main answer flow.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

# Upper bound for establishing a database connection.
CONNECT_TIMEOUT_SECONDS = 10

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _connect_args() -> dict[str, object]:
    """TLS settings for TiDB Cloud, when a CA certificate is available.

    ``connect_timeout`` bounds how long a broken network can stall a write,
    so the usage log can never hang a request.
    """
    settings = get_settings()
    ca_path = settings.ca_cert_file
    args: dict[str, object] = {"connect_timeout": CONNECT_TIMEOUT_SECONDS}
    if ca_path.is_file():
        args["ssl"] = {"ca": str(ca_path)}
    return args


def build_engine() -> Engine:
    """Create the engine lazily so import time performs no I/O."""
    settings = get_settings()
    return create_engine(
        settings.sqlalchemy_url,
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=settings.db_pool_recycle_seconds,
        pool_timeout=settings.db_pool_timeout_seconds,
        connect_args=_connect_args(),
        future=True,
    )


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = build_engine()
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(), autoflush=False, expire_on_commit=False
        )
    return _session_factory


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a request-scoped session."""
    db = get_session_factory()()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_connection() -> bool:
    """Return True when the database answers a trivial query."""
    try:
        db = get_session_factory()()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        return False
    return True
