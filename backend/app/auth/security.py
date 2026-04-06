"""Password hashing and JWT creation (no secret logging)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.settings import get_jwt_algorithm, get_jwt_secret, get_access_token_expire_minutes


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(*, user_id: uuid.UUID, email: str) -> str:
    secret = get_jwt_secret()
    if not secret:
        raise RuntimeError("JWT_SECRET is not configured")
    now = datetime.now(UTC)
    exp = now + timedelta(minutes=get_access_token_expire_minutes())
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=get_jwt_algorithm())


def decode_token(token: str) -> dict:
    secret = get_jwt_secret()
    if not secret:
        raise jwt.InvalidTokenError("JWT not configured")
    return jwt.decode(token, secret, algorithms=[get_jwt_algorithm()])
