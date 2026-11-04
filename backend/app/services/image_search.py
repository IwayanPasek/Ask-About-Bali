"""Image search through the Google Programmable Search Engine (Custom Search JSON API).

Only real results returned by Google are passed on to the client — nothing is
constructed locally, so no image URL or attribution can be invented.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

CUSTOM_SEARCH_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

# Only pages that plausibly belong to the Bali context are returned.
BALI_HINTS = (
    "bali",
    "balinese",
    "indonesia",
    "ubud",
    "uluwatu",
    "canggu",
    "seminyak",
    "kuta",
    "sanur",
    "nusa penida",
    "nusa lembongan",
    "gili",
    "tanah lot",
    "ulun danu",
    "mount batur",
    "mount agung",
    "jatiluwih",
    "tegallalang",
    "sidemen",
    "jimbaran",
    "gov.bali",
)


@dataclass(slots=True)
class ImageResult:
    """A single image plus its source attribution."""

    title: str
    image_url: str
    thumbnail_url: str
    source_name: str
    source_url: str

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "image_url": self.image_url,
            "thumbnail_url": self.thumbnail_url,
            "source_name": self.source_name,
            "source_url": self.source_url,
        }


def _is_bali_related(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in BALI_HINTS)


def _clean(text: str | None) -> str:
    return (text or "").strip()


def search_images(query: str, *, limit: int | None = None) -> list[ImageResult]:
    """Run an image search and return Bali-relevant results.

    Returns an empty list when the search is not configured, fails, or returns
    nothing usable — a failing image search must never break the text answer.
    """
    settings = get_settings()
    if not settings.google_search_api_key or not settings.google_search_engine_id:
        logger.info("Image search is not configured; skipping.")
        return []

    query = query.strip()
    if not query:
        return []

    max_results = limit or settings.google_search_max_results

    params = {
        "key": settings.google_search_api_key,
        "cx": settings.google_search_engine_id,
        "q": query,
        "searchType": "image",
        "num": str(max_results),
        "safe": "active",
        "gl": settings.google_search_country,
    }

    try:
        with httpx.Client(timeout=settings.google_search_timeout_seconds) as client:
            response = client.get(CUSTOM_SEARCH_ENDPOINT, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        logger.warning("Image search failed: %s", exc)
        return []
    except ValueError as exc:
        logger.warning("Image search returned a non-JSON body: %s", exc)
        return []

    items = payload.get("items") or []
    results: list[ImageResult] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        title = _clean(item.get("title"))
        image_url = _clean(item.get("link"))
        image_meta = item.get("image") or {}
        thumbnail_url = _clean(image_meta.get("thumbnailLink")) or image_url
        source_url = _clean(image_meta.get("contextLink"))
        source_name = _clean(item.get("displayLink")) or _clean(item.get("snippet"))

        if not image_url:
            continue

        # Keep the result set inside the Bali context.
        context_text = " ".join([title, source_name, source_url, thumbnail_url])
        if not _is_bali_related(context_text):
            continue

        if not source_name and source_url:
            source_name = source_url.split("/")[2] if "//" in source_url else source_url

        results.append(
            ImageResult(
                title=title,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                source_name=source_name,
                source_url=source_url,
            )
        )
        if len(results) >= max_results:
            break

    logger.info("Image search for %r returned %d Bali-relevant result(s).", query, len(results))
    return results
