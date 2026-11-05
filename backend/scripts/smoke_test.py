"""End-to-end smoke test for the ask endpoint with the upstream services mocked.

Run from the backend directory:

    ./.venv/Scripts/python.exe -m scripts.smoke_test
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from app.api import app  # noqa: E402
from app.services import gemini as gemini_module  # noqa: E402
from app.services import image_search, maps, web_search  # noqa: E402
from app.services.gemini import GeminiAnswer, GeminiResult, TokenUsage  # noqa: E402

ANSWER = GeminiAnswer(
    status="answered",
    answer="Tanah Lot adalah pura ikonik di Bali.",
    category="places",
    needs_image=True,
    image_query="Tanah Lot temple Bali",
    needs_location=True,
    location_query="Tanah Lot Temple",
    needs_web_search=True,
    web_query="Tanah Lot temple opening hours",
    search_tip="Cari 'Tanah Lot opening hours' di Google.",
)


def fake_ask_gemini(question, *, language, category=None):
    return GeminiResult(
        answer=ANSWER.model_copy(),
        usage=TokenUsage(prompt_tokens=100, output_tokens=50, total_tokens=150),
    )


def fake_search_images(query, *, limit=None):
    return [
        image_search.ImageResult(
            title="Tanah Lot",
            image_url="https://example.test/tanah-lot.jpg",
            thumbnail_url="https://example.test/tanah-lot-thumb.jpg",
            source_name="www.bali.com",
            source_url="https://www.bali.com/tanah-lot/",
        )
    ]


def fake_search_places(query, *, limit=None):
    return [
        maps.PlaceResult(
            place_id="ChIJ123",
            name="Tanah Lot Temple",
            address="Jl. Goa Lempeh, Canggu, Bali",
            latitude=-8.6212,
            longitude=115.0870,
            maps_url="https://www.google.com/maps/search/?api=1&query=Tanah+Lot",
        )
    ]


def fake_search_web(query, *, limit=None):
    return [
        web_search.WebResult(
            title="Tanah Lot opening hours",
            link="https://www.bali.com/tanah-lot-hours/",
            snippet="Open daily from 6am to 7pm.",
            source_name="www.bali.com",
        )
    ]


def main() -> int:
    gemini_module.ask_gemini = fake_ask_gemini
    image_search.search_images = fake_search_images
    maps.search_places = fake_search_places
    web_search.search_web = fake_search_web

    import app.routers.ask as ask_router

    ask_router.ask_gemini = fake_ask_gemini
    ask_router.search_images = fake_search_images
    ask_router.search_places = fake_search_places
    ask_router.search_web = fake_search_web

    # The usage log is stubbed out so this test never writes to a real database.
    logged: list[dict[str, object]] = []

    def fake_log_question(**kwargs):
        logged.append(kwargs)

    ask_router.log_question = fake_log_question

    client = TestClient(app)
    failures: list[str] = []

    health = client.get("/api/health")
    if health.status_code != 200:
        failures.append(f"GET /api/health -> {health.status_code}")
    else:
        print("health:", health.json())

    response = client.post(
        "/api/ask",
        json={"question": "Ceritakan tentang Tanah Lot", "language": "id"},
        headers={"X-Session-Id": "test-session-123"},
    )
    if response.status_code != 200:
        failures.append(f"POST /api/ask -> {response.status_code}: {response.text}")
    else:
        body = response.json()
        print("ask:", body)
        expected = {
            "status": "answered",
            "images": 1,
            "locations": 1,
            "sources": 1,
        }
        if body.get("status") != expected["status"]:
            failures.append(f"status -> {body.get('status')}")
        if len(body.get("images", [])) != expected["images"]:
            failures.append("images missing")
        if len(body.get("locations", [])) != expected["locations"]:
            failures.append("locations missing")
        if len(body.get("sources", [])) != expected["sources"]:
            failures.append("sources missing")
        if not body.get("search_tip"):
            failures.append("search_tip missing")

    if len(logged) != 1:
        failures.append(f"usage log calls -> {len(logged)} (expected 1)")
    else:
        record = logged[0]
        print("logged:", {k: record[k] for k in ("status", "language", "model_id")})
        if record.get("session_id") != "test-session-123":
            failures.append("session id not forwarded to the log")
        if record.get("image_count") != 1 or record.get("source_count") != 1:
            failures.append("counts not forwarded to the log")

    empty = client.post("/api/ask", json={"question": "   "})
    if empty.status_code != 422:
        failures.append(f"empty question -> {empty.status_code} (expected 422)")

    invalid = client.post("/api/ask", json={"question": "hi", "language": "fr"})
    if invalid.status_code != 422:
        failures.append(f"bad language -> {invalid.status_code} (expected 422)")

    if failures:
        print("\nFAILURES:")
        for item in failures:
            print(" -", item)
        return 1

    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
