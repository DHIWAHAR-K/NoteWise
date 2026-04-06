from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DbHealth(Base):
    """Minimal table to verify PostgreSQL connectivity and migrations."""

    __tablename__ = "db_health"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ok: Mapped[bool] = mapped_column(default=True)
