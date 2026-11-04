"""Ask endpoint: turns a user question into an answer scoped to Bali.

When the answer benefits from supporting material, the backend also runs an
image search, a place lookup, and a web search through Google, and attaches the
results with their source attribution.
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, BackgroundTasks, Header

from app.config import get_settings
from app.errors import ValidationError
from app.schemas import (
    AskRequest,
    AskResponse,
    ImageResultModel,
    LocationResultModel,
    SourceResultModel,
)
from app.services.gemini import GeminiAnswer, ask_gemini
from app.services.image_search import search_images
from app.services.maps import MapsLookupError, search_places
from app.services.usage_log import elapsed_ms, log_question
from app.services.web_search import search_web

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ask"])

# Fallback messages, used only when the model returns an empty answer body.
FALLBACK_NOT_FOUND = {
    "id": "Data tidak ditemukan pada sistem.",
    "en": "The requested data was not found on the system.",
}

FALLBACK_OUT_OF_SCOPE = {
    "id": (
        "Layanan ini hanya menyediakan informasi terkait Bali. "
        "Silakan ajukan pertanyaan tentang Bali."
    ),
    "en": (
        "This service only provides information related to Bali. "
        "Please ask a question about Bali."
    ),
}

# Browser session id, used only to group anonymous usage logs. It is hashed
# before it reaches the database.
SESSION_HEADER = "X-Session-Id"


def _localised(mapping: dict[str, str], language: str) -> str:
    return mapping.get(language, mapping["id"])


def _normalise(result: GeminiAnswer, language: str) -> AskResponse:
    """Map the model output onto the API contract, filling in safe defaults."""
    settings = get_settings()
    status = (result.status or "").strip().lower()
    answer = (result.answer or "").strip()
    category = (result.category or "other").strip().lower() or "other"

    if status not in {"answered", "out_of_scope", "not_found"}:
        logger.warning("Gemini returned an unexpected status: %s", status)
        status = "answered"

    if status == "out_of_scope" and not answer:
        answer = _localised(FALLBACK_OUT_OF_SCOPE, language)

    if status == "not_found" and not answer:
        answer = _localised(FALLBACK_NOT_FOUND, language)

    if status == "answered" and not answer:
        status = "not_found"
        answer = _localised(FALLBACK_NOT_FOUND, language)

    return AskResponse(
        status=status,  # type: ignore[arg-type]
        answer=answer,
        language=language,
        category=category,
        model_id=settings.gemini_model_id,
    )


def _collect_images(result: GeminiAnswer, response: AskResponse) -> list[ImageResultModel]:
    """Attach image results, but only for in-scope answers that need a photo."""
    if response.status != "answered" or not result.needs_image:
        return []

    query = (result.image_query or "").strip()
    if not query:
        return []

    try:
        found = search_images(query)
    except Exception:  # image search must never break the text answer
        logger.exception("Unexpected failure during image search.")
        return []

    return [
        ImageResultModel(
            title=item.title,
            image_url=item.image_url,
            thumbnail_url=item.thumbnail_url,
            source_name=item.source_name,
            source_url=item.source_url,
        )
        for item in found
    ]


def _collect_locations(result: GeminiAnswer, response: AskResponse) -> str | None:
    """Attach place results. Returns a polite message when the lookup failed.

    A failed place lookup must not break the text answer, so the error is
    reported separately and the answer stays intact.
    """
    if response.status != "answered" or not result.needs_location:
        return None

    query = (result.location_query or "").strip()
    if not query:
        return None

    try:
        found = search_places(query)
    except MapsLookupError as exc:
        logger.warning("Place lookup failed: %s", exc)
        return str(exc)
    except Exception:
        logger.exception("Unexpected failure during place lookup.")
        return "Informasi lokasi belum dapat dimuat saat ini. Silakan coba lagi."

    response.locations = [
        LocationResultModel(
            place_id=item.place_id,
            name=item.name,
            address=item.address,
            latitude=item.latitude,
            longitude=item.longitude,
            maps_url=item.maps_url,
        )
        for item in found
    ]
    return None


def _collect_sources(result: GeminiAnswer, response: AskResponse) -> str | None:
    """Attach web sources. Returns a polite message when the search failed.

    A failed web search must not break the text answer, so the error is
    reported separately and the answer stays intact.
    """
    if response.status != "answered" or not result.needs_web_search:
        return None

    query = (result.web_query or "").strip()
    if not query:
        return None

    try:
        found = search_web(query)
    except Exception:
        logger.exception("Unexpected failure during web search.")
        return "Informasi web belum dapat dimuat saat ini. Silakan coba lagi."

    response.sources = [
        SourceResultModel(
            title=item.title,
            link=item.link,
            snippet=item.snippet,
            source_name=item.source_name,
        )
        for item in found
    ]
    return None


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    background_tasks: BackgroundTasks,
    x_session_id: str | None = Header(default=None, alias=SESSION_HEADER),
) -> AskResponse:
    """Answer a question about Bali, with supporting images, places, and sources.

    Questions outside the Bali scope are refused by the model with a clear
    explanation. Upstream quota failures surface as a 503 with a
    "please try again later" message.
    """
    question = payload.question.strip()
    if not question:
        raise ValidationError("Pertanyaan tidak boleh kosong.")

    started_at = time.monotonic()

    gemini_result = ask_gemini(
        question, language=payload.language, category=payload.category
    )
    result = gemini_result.answer

    response = _normalise(result, payload.language)
    response.images = _collect_images(result, response)
    response.location_error = _collect_locations(result, response)
    response.web_search_error = _collect_sources(result, response)
    response.search_tip = (result.search_tip or "").strip() or None

    # The usage log is written after the response, so a slow or unreachable
    # database never delays the traveller's answer.
    background_tasks.add_task(
        log_question,
        question=question,
        answer=response.answer,
        language=response.language,
        category=response.category,
        status=response.status,
        model_id=response.model_id,
        session_id=x_session_id,
        usage=gemini_result.usage,
        latency_ms=elapsed_ms(started_at),
        image_count=len(response.images),
        location_count=len(response.locations),
        source_count=len(response.sources),
    )

    return response
