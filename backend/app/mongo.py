"""Async MongoDB client (Motor). Does not log connection strings or message bodies."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect(uri: str) -> None:
    global _client, _db
    await disconnect()
    _client = AsyncIOMotorClient(uri)
    _db = _client.get_default_database()


async def disconnect() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB not configured")
    return _db


def is_configured() -> bool:
    return _db is not None
