"""Alembic migration environment (async SQLAlchemy + asyncpg)."""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv

# Ensure backend/ is on path when running `alembic` from backend directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv()

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.db.base import Base
from app.db import models  # noqa: F401
from app.settings import get_database_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    raise RuntimeError("Offline migrations are not supported for this project.")


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    url = get_database_url()
    if not url:
        raise RuntimeError("Set DATABASE_URL or POSTGRES_HOST/POSTGRES_* for migrations.")
    ini_section = config.get_section(config.config_ini_section) or {}
    ini_section["sqlalchemy.url"] = url
    connectable = async_engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
