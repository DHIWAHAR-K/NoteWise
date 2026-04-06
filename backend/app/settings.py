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


def get_jwt_secret() -> str | None:
    s = os.getenv("JWT_SECRET", "").strip()
    return s or None


def get_jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256").strip() or "HS256"


def get_access_token_expire_minutes() -> int:
    raw = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080").strip()
    try:
        n = int(raw)
        return max(5, min(n, 60 * 24 * 30))
    except ValueError:
        return 10080


def get_moonshot_api_key() -> str | None:
    s = os.getenv("MOONSHOT_API_KEY", "").strip()
    return s or None


def get_moonshot_base_url() -> str:
    return (
        os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1").strip()
        or "https://api.moonshot.ai/v1"
    ).rstrip("/")


def get_moonshot_vision_model() -> str:
    return (
        os.getenv("MOONSHOT_VISION_MODEL", "moonshot-v1-8k-vision-preview").strip()
        or "moonshot-v1-8k-vision-preview"
    )


def clear_settings_cache() -> None:
    get_database_url.cache_clear()
    get_mongodb_uri.cache_clear()
