"""Error envelope shared by every failure response.

Messages returned to the client are written for end users and never contain
API keys, credentials, or raw upstream error details.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for errors that map to a clean JSON envelope."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        # `detail` is for server-side logs only; it is never sent to the client.
        self.detail = detail

    def to_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={"error": {"code": self.code, "message": self.message}},
        )


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class UpstreamError(AppError):
    status_code = 502
    code = "upstream_error"


class ServiceBusyError(AppError):
    """Quota exhausted or rate limited: the caller should retry later."""

    status_code = 503
    code = "service_busy"


class ServiceUnavailableError(AppError):
    status_code = 503
    code = "service_unavailable"


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return exc.to_response()
