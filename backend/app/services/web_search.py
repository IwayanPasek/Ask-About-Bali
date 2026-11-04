"""Web search through the Google Programmable Search Engine (Custom Search JSON API).

Returns the original result links so the traveller can open the source.
Nothing is generated locally — only real results from Google are passed on.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

CUSTOM_SEARCH_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

# Only sources that plausibly belong to the Bali context are returned.
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
    "bali.",
    ".bali",
    "go.id",
)


@dataclass(slots=True)
class WebResult:
    """A single web result with its original link."""

    title: str
    link: str
    snippet: str
    source_name: str

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "source_name": self.source_name,
        }


def _is_bali_related(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in BALI_HINTS)


def _clean(text: str | None) -> str:
    return (text or "").strip()


def search_web(query: str, *, limit: int | None = None) -> list[WebResult]:
    """Run a web search and return Bali-relevant results with source links.

    Returns an empty list when the search is not configured, fails, or returns
    nothing usable — a failing web search must never break the text answer.
    """
    settings = get_settings()
    if not settings.google_search_api_key or not settings.google_search_engine_id:
        logger.info("Web search is not configured; skipping.")
        return []

    query = query.strip()
    if not query:
        return []

    max_results = limit or settings.google_search_max_results

    params = {
        "key": settings.google_search_api_key,
        "cx": settings.google_search_engine_id,
        "q": query,
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
        logger.warning("Web search failed: %s", exc)
        return []
    except ValueError as exc:
        logger.warning("Web search returned a non-JSON body: %s", exc)
        return []

    items = payload.get("items") or []
    results: list[WebResult] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        title = _clean(item.get("title"))
        link = _clean(item.get("link"))
        snippet = _clean(item.get("snippet"))
        source_name = _clean(item.get("displayLink"))

        if not link:
            continue

        # Keep the result set inside the Bali context.
        if not _is_bali_related(" ".join([title, link, snippet, source_name])):
            continue

        if not source_name:
            source_name = link.split("/")[2] if "//" in link else link

        results.append(
            WebResult(title=title, link=link, snippet=snippet, source_name=source_name)
        )
        if len(results) >= max_results:
            break

    logger.info("Web search for %r returned %d Bali-relevant result(s).", query, len(results))
    return results
