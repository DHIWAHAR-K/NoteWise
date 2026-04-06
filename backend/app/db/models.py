import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, true as sa_true
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DbHealth(Base):
    """Minimal table to verify PostgreSQL connectivity and migrations."""

    __tablename__ = "db_health"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ok: Mapped[bool] = mapped_column(default=True)


class User(Base):
    """Registered user for JWT auth (Mark 3)."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=sa_true()
    )
