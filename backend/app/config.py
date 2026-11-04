"""Application settings, loaded from environment variables / .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Stage-3 configuration: Gemini integration for text answers."""

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Ask About Bali API"
    app_version: str = "0.1.0"
    environment: str = "development"

    # --- Google Gemini ---
    gemini_api_key: str = ""
    gemini_model_id: str = "gemini-3.5-flash-lite"
    gemini_timeout_seconds: int = 30
    # Token saving: a hard ceiling on the answer size, so a single question can
    # never burn the quota on a runaway generation.
    gemini_max_output_tokens: int = 900

    # --- Google Programmable Search Engine (web + image search) ---
    google_search_api_key: str = ""
    google_search_engine_id: str = ""
    google_search_max_results: int = 6
    google_search_timeout_seconds: int = 8
    google_search_country: str = "id"

    # --- Google Maps (Places API) ---
    google_maps_api_key: str = ""
    google_maps_timeout_seconds: int = 8
    google_maps_max_results: int = 5
    google_maps_language: str = "id"
    google_maps_region: str = "ID"

    # --- TiDB Cloud (MVP: anonymous usage log) ---
    tidb_host: str = ""
    tidb_port: int = 4000
    tidb_user: str = ""
    tidb_password: str = ""
    tidb_database: str = ""
    tidb_ca_cert_path: str = str(BACKEND_DIR / "certs" / "ca.pem")
    database_url: str = ""  # full override; wins over the tidb_* vars
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_pool_recycle_seconds: int = 1800
    db_pool_timeout_seconds: int = 5

    # Salt used to hash the browser session id before it is stored.
    session_hash_salt: str = ""

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key.strip())

    @property
    def ca_cert_file(self) -> Path:
        """Resolve the TiDB CA certificate path.

        A relative path is resolved against the project root, so the value in
        ``.env`` works no matter which directory the server is started from.
        """
        configured = Path(self.tidb_ca_cert_path).expanduser()
        if configured.is_absolute():
            return configured
        return (PROJECT_ROOT / configured).resolve()

    @property
    def has_database_config(self) -> bool:
        return bool(self.database_url or (self.tidb_host and self.tidb_user and self.tidb_database))

    @property
    def sqlalchemy_url(self) -> str:
        """Build the SQLAlchemy URL for TiDB Cloud (MySQL-compatible)."""
        if self.database_url:
            return self.database_url
        if not self.has_database_config:
            raise RuntimeError(
                "Database is not configured. Set DATABASE_URL or the TIDB_* environment variables."
            )
        return str(
            URL.create(
                drivername="mysql+pymysql",
                username=self.tidb_user,
                password=self.tidb_password,
                host=self.tidb_host,
                port=self.tidb_port,
                database=self.tidb_database,
                query={"charset": "utf8mb4"},
            )
        )

    def missing_credentials(self) -> list[str]:
        """Names of the environment variables that are not set yet."""
        missing = []
        for name in (
            "GEMINI_API_KEY",
            "GOOGLE_SEARCH_API_KEY",
            "GOOGLE_SEARCH_ENGINE_ID",
            "GOOGLE_MAPS_API_KEY",
            "TIDB_HOST",
            "TIDB_USER",
            "TIDB_PASSWORD",
            "TIDB_DATABASE",
        ):
            value = getattr(self, name.lower())
            if not str(value).strip():
                missing.append(name)
        return missing


@lru_cache
def get_settings() -> Settings:
    return Settings()
