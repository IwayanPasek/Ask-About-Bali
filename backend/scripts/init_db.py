"""Create the TiDB Cloud tables used by the anonymous usage log.

Run it once, after the TiDB credentials are configured in ``.env``:

    python -m scripts.init_db

The script is idempotent: existing tables are left untouched.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Make `app` importable when the script is run from the backend directory.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings  # noqa: E402
from app.db.models import Base  # noqa: E402
from app.db.session import build_engine, check_connection  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("init_db")


def main() -> int:
    settings = get_settings()
    if not settings.has_database_config:
        logger.error(
            "Database is not configured. Set DATABASE_URL or the TIDB_* variables in .env."
        )
        return 1

    logger.info("Checking the database connection…")
    if not check_connection():
        logger.error("Could not reach the database. Check the credentials and the CA certificate.")
        return 1

    logger.info("Creating tables (if they do not exist yet)…")
    Base.metadata.create_all(bind=build_engine())
    logger.info("Done. Tables: %s", ", ".join(sorted(Base.metadata.tables)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
