"""Environment-backed settings. Does not log secrets."""

from __future__ import annotations

import os
from functools import lru_cache
from urllib.parse import quote_plus


def _build_postgres_url_async() -> str | None:
    explicit = os.getenv("DATABASE_URL")
    if explicit and explicit.strip():
        return explicit.strip()
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    if not all([host, user, password, db]):
        return None
    return (
        f"postgresql+asyncpg://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{db}"
    )


def _build_mongodb_uri() -> str | None:
    explicit = os.getenv("MONGODB_URI")
    if explicit and explicit.strip():
        return explicit.strip()
    host = os.getenv("MONGODB_HOST")
    port = os.getenv("MONGODB_PORT", "27017")
    user = os.getenv("MONGO_ROOT_USER")
    password = os.getenv("MONGO_ROOT_PASSWORD")
    if not all([host, user, password]):
        return None
    # Database name `notewise` for application collections (e.g. conversations).
    return (
        f"mongodb://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/notewise"
        f"?authSource=admin"
    )


@lru_cache
def get_database_url() -> str | None:
    return _build_postgres_url_async()


@lru_cache
def get_mongodb_uri() -> str | None:
    return _build_mongodb_uri()


def clear_settings_cache() -> None:
    get_database_url.cache_clear()
    get_mongodb_uri.cache_clear()
