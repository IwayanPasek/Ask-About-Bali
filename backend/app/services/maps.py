"""Place lookup through the Google Maps Platform (Places API, Text Search).

Only real places returned by Google are passed on to the client — the service
never constructs a place, coordinate, or address locally.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

PLACES_TEXT_SEARCH_ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

# Only places whose address or coordinates fall inside this rectangle are kept,
# so a lookup can never drift outside the Bali context.
BALI_BOUNDS = {
    "min_lat": -8.85,
    "max_lat": -8.05,
    "min_lng": 114.40,
    "max_lng": 115.80,
}

# Places API v1 text search: only the fields we actually use.
FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.location,places.googleMapsUri"


@dataclass(slots=True)
class PlaceResult:
    """A single place plus the data needed to render it."""

    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    maps_url: str

    def to_dict(self) -> dict[str, object]:
        return {
            "place_id": self.place_id,
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "maps_url": self.maps_url,
        }


class MapsLookupError(Exception):
    """Raised when the Maps API call fails; the message is safe for users."""


def _in_bali_bounds(latitude: float, longitude: float) -> bool:
    return (
        BALI_BOUNDS["min_lat"] <= latitude <= BALI_BOUNDS["max_lat"]
        and BALI_BOUNDS["min_lng"] <= longitude <= BALI_BOUNDS["max_lng"]
    )


def _clean(text: str | None) -> str:
    return (text or "").strip()


def search_places(query: str, *, limit: int | None = None) -> list[PlaceResult]:
    """Look up a place by name and return the Bali-relevant matches.

    Raises :class:`MapsLookupError` when the API is not configured or the call
    fails, so the caller can show a polite message without technical detail.
    """
    settings = get_settings()
    if not settings.google_maps_api_key:
        raise MapsLookupError("Layanan peta belum dikonfigurasi.")

    query = query.strip()
    if not query:
        return []

    max_results = limit or settings.google_maps_max_results

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_maps_api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body = {
        "textQuery": query,
        "languageCode": settings.google_maps_language,
        "regionCode": settings.google_maps_region,
        "maxResultCount": max(max_results * 2, 10),
    }

    try:
        with httpx.Client(timeout=settings.google_maps_timeout_seconds) as client:
            response = client.post(PLACES_TEXT_SEARCH_ENDPOINT, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        logger.warning("Google Maps request failed with status %s.", status)
        if status in (401, 403):
            raise MapsLookupError(
                "Layanan peta belum dapat diakses saat ini. Silakan coba lagi nanti."
            ) from exc
        if status == 429:
            raise MapsLookupError(
                "Permintaan ke layanan peta terlalu sering. Silakan coba lagi beberapa saat lagi."
            ) from exc
        raise MapsLookupError(
            "Informasi lokasi belum dapat dimuat saat ini. Silakan coba lagi."
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning("Google Maps request could not be sent: %s", exc)
        raise MapsLookupError(
            "Informasi lokasi belum dapat dimuat saat ini. Silakan coba lagi."
        ) from exc
    except ValueError as exc:
        logger.warning("Google Maps returned a non-JSON body: %s", exc)
        raise MapsLookupError(
            "Informasi lokasi belum dapat dimuat saat ini. Silakan coba lagi."
        ) from exc

    places = payload.get("places") or []
    results: list[PlaceResult] = []

    for place in places:
        if not isinstance(place, dict):
            continue

        location = place.get("location") or {}
        try:
            latitude = float(location["latitude"])
            longitude = float(location["longitude"])
        except (KeyError, TypeError, ValueError):
            continue

        # Keep the result set inside the Bali context.
        if not _in_bali_bounds(latitude, longitude):
            continue

        name = _clean((place.get("displayName") or {}).get("text"))
        address = _clean(place.get("formattedAddress"))
        place_id = _clean(place.get("id"))
        maps_url = _clean(place.get("googleMapsUri"))

        if not name or not place_id:
            continue

        if not maps_url:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

        results.append(
            PlaceResult(
                place_id=place_id,
                name=name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                maps_url=maps_url,
            )
        )
        if len(results) >= max_results:
            break

    logger.info("Place lookup for %r returned %d Bali-relevant result(s).", query, len(results))
    return results
