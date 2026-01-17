"""Job model for tracking worksheet processing status."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker

from app.core.config import settings


class JobStatus(str, Enum):
    """Job status values."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


class Job(Base):
    """Job model for tracking worksheet processing status."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worksheet_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=JobStatus.QUEUED.value)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert job to dictionary for API responses."""
        return {
            "id": self.id,
            "worksheet_id": self.worksheet_id,
            "user_id": self.user_id,
            "status": self.status,
            "progress": self.progress,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# Database engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None and settings.database_url:
        _engine = create_engine(settings.database_url, echo=settings.debug)
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        if engine:
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


def init_db():
    """Initialise the database (create tables)."""
    engine = get_engine()
    if engine:
        Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get a database session."""
    SessionLocal = get_session_factory()
    if not SessionLocal:
        raise RuntimeError("Database not configured (DATABASE_URL not set)")
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise
