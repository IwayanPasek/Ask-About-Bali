"""Gemini client wrapper (google-genai SDK).

Turns upstream failures into the two user-facing situations we must handle
distinctly:

* quota / rate limit reached -> :class:`ServiceBusyError` (retry later)
* anything else upstream     -> :class:`UpstreamError`

Technical details (API keys, raw upstream payloads) are kept in the `detail`
attribute, which is logged server-side and never returned to the client.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

from app.config import get_settings
from app.errors import ServiceBusyError, UpstreamError
from app.services.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Upstream status codes that mean "we are out of quota / being rate limited".
BUSY_STATUS_CODES = {429}
# Codes that mean the account itself cannot serve requests right now.
UNAVAILABLE_STATUS_CODES = {500, 502, 503, 504}

# How long the service refuses new work after a quota/rate-limit failure.
BUSY_COOLDOWN_SECONDS = 60


class GeminiAnswer(BaseModel):
    """Structured output the model is asked to return."""

    status: str = Field(description="answered, out_of_scope, or not_found")
    answer: str = Field(default="", description="The answer text for the user.")
    category: str = Field(default="other", description="Short topic label in English.")
    needs_image: bool = Field(
        default=False, description="True when a supporting photo would help the traveller."
    )
    image_query: str = Field(
        default="", description="Search keywords for the supporting image; empty when not needed."
    )
    needs_location: bool = Field(
        default=False, description="True when a concrete, findable place in Bali should be shown."
    )
    location_query: str = Field(
        default="", description="Name of the specific place in Bali; empty when not needed."
    )
    needs_web_search: bool = Field(
        default=False, description="True when current or official sources would help."
    )
    web_query: str = Field(
        default="", description="Search keywords for supporting web sources; empty when not needed."
    )
    search_tip: str = Field(
        default="", description="Short tip on how the traveller can verify this themselves."
    )


class _BusyGate:
    """Fail-fast gate that stops calling Gemini while the quota is exhausted."""

    def __init__(self) -> None:
        self._until: float = 0.0
        self._lock = threading.Lock()

    def is_busy(self) -> bool:
        with self._lock:
            return time.monotonic() < self._until

    def trip(self, seconds: int = BUSY_COOLDOWN_SECONDS) -> None:
        with self._lock:
            self._until = max(self._until, time.monotonic() + seconds)

    def reset(self) -> None:
        with self._lock:
            self._until = 0.0


busy_gate = _BusyGate()

_client: genai.Client | None = None
_client_lock = threading.Lock()


def get_client() -> genai.Client:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                settings = get_settings()
                if not settings.has_gemini_key:
                    raise UpstreamError(
                        "Layanan AI belum dikonfigurasi. Silakan coba lagi nanti."
                    )
                _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _extract_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text
    return ""


@dataclass(slots=True)
class TokenUsage:
    """Token accounting for a single Gemini call."""

    prompt_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(slots=True)
class GeminiResult:
    """The model's answer plus its token usage."""

    answer: GeminiAnswer
    usage: TokenUsage


def _extract_usage(response: Any) -> TokenUsage:
    """Read token counts from the response metadata, if the model reported them."""
    metadata = getattr(response, "usage_metadata", None)
    if metadata is None:
        return TokenUsage()
    return TokenUsage(
        prompt_tokens=getattr(metadata, "prompt_token_count", None),
        output_tokens=getattr(metadata, "candidates_token_count", None),
        total_tokens=getattr(metadata, "total_token_count", None),
    )


def ask_gemini(
    question: str,
    *,
    language: str,
    category: str | None = None,
) -> GeminiResult:
    """Send a question to Gemini and return the structured answer.

    Raises :class:`ServiceBusyError` when the quota or API limit is reached and
    :class:`UpstreamError` for any other upstream failure.
    """
    if busy_gate.is_busy():
        raise ServiceBusyError(
            "Sistem sedang sibuk dan batas permintaan sementara tercapai. "
            "Silakan coba lagi beberapa saat lagi."
        )

    settings = get_settings()
    client = get_client()

    language_name = "Bahasa Indonesia" if language == "id" else "English"
    instruction = f"Answer the user's question in {language_name}."
    if category:
        instruction += f" The user selected the category: {category}."

    try:
        response = client.models.generate_content(
            model=settings.gemini_model_id,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=f"{SYSTEM_PROMPT}\n\n{instruction}",
                response_mime_type="application/json",
                response_schema=GeminiAnswer,
                temperature=0.3,
                max_output_tokens=settings.gemini_max_output_tokens,
                http_options=types.HttpOptions(timeout=settings.gemini_timeout_seconds * 1000),
            ),
        )
    except errors.APIError as exc:
        code = getattr(exc, "code", None)
        if code in BUSY_STATUS_CODES:
            busy_gate.trip()
            logger.warning("Gemini quota/rate limit reached (code=%s).", code)
            raise ServiceBusyError(
                "Sistem sedang sibuk dan batas permintaan sementara tercapai. "
                "Silakan coba lagi beberapa saat lagi.",
                detail=str(exc),
            ) from exc
        if code in UNAVAILABLE_STATUS_CODES:
            logger.error("Gemini temporarily unavailable (code=%s).", code)
            raise UpstreamError(
                "Layanan AI sedang tidak tersedia. Silakan coba lagi sebentar.",
                detail=str(exc),
            ) from exc
        logger.error("Gemini call failed (code=%s).", code)
        raise UpstreamError(
            "Maaf, permintaan Anda belum dapat diproses. Silakan coba lagi.",
            detail=str(exc),
        ) from exc
    except Exception as exc:  # timeouts, transport errors, unexpected shapes
        logger.exception("Unexpected failure while calling Gemini.")
        raise UpstreamError(
            "Maaf, permintaan Anda belum dapat diproses. Silakan coba lagi.",
            detail=str(exc),
        ) from exc

    usage = _extract_usage(response)

    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, GeminiAnswer):
        return GeminiResult(answer=parsed, usage=usage)

    text = _extract_text(response)
    if not text:
        raise UpstreamError(
            "Maaf, permintaan Anda belum dapat diproses. Silakan coba lagi."
        )

    try:
        return GeminiResult(answer=GeminiAnswer.model_validate_json(text), usage=usage)
    except Exception as exc:
        logger.error("Gemini returned an unparsable payload.")
        raise UpstreamError(
            "Maaf, permintaan Anda belum dapat diproses. Silakan coba lagi.",
            detail=str(exc),
        ) from exc
