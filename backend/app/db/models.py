"""SQLAlchemy models for the TiDB Cloud tables used by the MVP."""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Index, Integer, SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Naive UTC timestamp (TiDB DATETIME columns are timezone-less)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class QuestionLog(Base):
    """Anonymous record of one question/answer exchange.

    Stores only what is needed to understand usage. No API keys, no
    credentials, and no personal data: the browser session id is stored as a
    salted hash, and the raw id never reaches the database.
    """

    __tablename__ = "question_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="id")
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="answered")
    model_id: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    location_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    source_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (Index("idx_log_session_created", "session_hash", "created_at"),)
