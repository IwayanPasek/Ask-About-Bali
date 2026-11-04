"""FastAPI application entry point for Ask About Bali.

Serves the ask endpoint with Gemini answers plus supporting images, places,
and web sources, and an anonymous usage log in TiDB Cloud.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.errors import AppError, app_error_handler
from app.routers import ask

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API untuk aplikasi Ask About Bali — asisten informasi Bali berbasis AI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ask.router)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    if exc.detail:
        logging.getLogger(__name__).error("AppError %s: %s", exc.code, exc.detail)
    return await app_error_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Permintaan tidak valid.",
            }
        },
    )


@app.get("/api/health", tags=["system"])
def health() -> dict[str, object]:
    """Return the application status and which environment variables are still missing."""
    configured = []
    if settings.has_gemini_key:
        configured.append("gemini")
    if settings.google_search_api_key and settings.google_search_engine_id:
        configured.append("google_search")
    if settings.google_maps_api_key:
        configured.append("google_maps")
    if settings.has_database_config:
        configured.append("tidb")

    database_reachable: bool | None = None
    if settings.has_database_config:
        from app.db.session import check_connection

        database_reachable = check_connection()

    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "configured_services": configured,
        "missing_environment_variables": settings.missing_credentials(),
        "model_id": settings.gemini_model_id,
        "database_reachable": database_reachable,
    }


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
