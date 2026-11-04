"""Pydantic request/response schemas for the API."""

from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["id", "en"]
AskStatus = Literal["answered", "out_of_scope", "not_found"]


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Pertanyaan pengguna tentang Bali.",
    )
    language: Language = Field(default="id", description="Bahasa jawaban: 'id' atau 'en'.")
    category: str | None = Field(
        default=None,
        max_length=100,
        description="Kategori opsional, misalnya 'culture' atau 'transport'.",
    )


class ImageResultModel(BaseModel):
    title: str
    image_url: str
    thumbnail_url: str
    source_name: str
    source_url: str


class LocationResultModel(BaseModel):
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    maps_url: str


class SourceResultModel(BaseModel):
    title: str
    link: str
    snippet: str
    source_name: str


class AskResponse(BaseModel):
    status: AskStatus
    answer: str
    language: str
    category: str | None = None
    model_id: str
    images: list[ImageResultModel] = Field(default_factory=list)
    locations: list[LocationResultModel] = Field(default_factory=list)
    location_error: str | None = Field(
        default=None,
        description="Pesan sopan bila pencarian lokasi gagal; tidak pernah berisi detail teknis.",
    )
    sources: list[SourceResultModel] = Field(default_factory=list)
    search_tip: str | None = Field(
        default=None,
        description="Tips singkat cara memverifikasi informasi secara mandiri.",
    )
    web_search_error: str | None = Field(
        default=None,
        description="Pesan sopan bila pencarian web gagal; tidak pernah berisi detail teknis.",
    )


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str
    configured_services: list[str]
    missing_environment_variables: list[str]
