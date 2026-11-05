"""Entrypoint for the Vercel Python runtime.

Vercel builds this file as a serverless function that fronts the whole
FastAPI application. It lives in the ``backend`` folder so that the
application package (``app``) is importable without extra path juggling, and
next to ``requirements.txt`` so the builder picks up the dependencies.

The Vercel framework preset serves every request through the ``app`` object
exported below, with the request path unchanged. The middleware is a safety
net for the cases where the path arrives without the ``/api`` prefix that the
FastAPI routers use.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.api import app  # noqa: E402  (path setup must run first)

# The prefix every API route is registered under.
_API_PREFIX = "/api"

# Paths that are not part of the API surface and must be left alone, so the
# interactive documentation keeps working.
_PASSTHROUGH_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/favicon.ico")

# Mount points the runtime may prepend to the path before handing it over.
_MOUNT_PREFIXES = ("/backend", _API_PREFIX)


def _normalise_path(path: str) -> str:
    """Return the path in the form the FastAPI routers expect."""
    if not path or path == "/":
        return "/"
    if path.startswith(_PASSTHROUGH_PREFIXES):
        return path

    # Remove every mount point the runtime may have prepended, then put the
    # API prefix back exactly once.
    changed = True
    while changed:
        changed = False
        for prefix in _MOUNT_PREFIXES:
            if path == prefix:
                return _API_PREFIX
            if path.startswith(prefix + "/"):
                path = path[len(prefix) :]
                changed = True
                break

    return _API_PREFIX + path


class ApiPathMiddleware:
    """Normalise the request path before it reaches FastAPI.

    A pure ASGI middleware, so it sees the raw scope. Only the path is
    touched: method, headers, query string, and body pass through unchanged.
    """

    def __init__(self, app):  # type: ignore[no-untyped-def]
        self.app = app

    async def __call__(self, scope, receive, send):  # type: ignore[no-untyped-def]
        if scope.get("type") == "http":
            normalised = _normalise_path(scope.get("path", ""))
            if normalised != scope.get("path"):
                scope = {**scope, "path": normalised}
        await self.app(scope, receive, send)


# Added before the app starts serving, so the middleware stack is still
# mutable at this point.
app.add_middleware(ApiPathMiddleware)
