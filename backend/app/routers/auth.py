"""User registration and JWT login. NOT for clinical use."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, hash_password, verify_password
from app.auth.deps import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.settings import get_jwt_secret

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=256)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=256)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    is_active: bool


@router.post("/register", response_model=TokenOut)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_db_session)):
    if not get_jwt_secret():
        raise HTTPException(status_code=503, detail="Authentication is not configured on this server.")
    user = User(
        email=body.email.lower().strip(),
        password_hash=hash_password(body.password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from None
    await session.refresh(user)
    token = create_access_token(user_id=user.id, email=user.email)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, session: AsyncSession = Depends(get_db_session)):
    if not get_jwt_secret():
        raise HTTPException(status_code=503, detail="Authentication is not configured on this server.")
    result = await session.execute(select(User).where(User.email == body.email.lower().strip()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    token = create_access_token(user_id=user.id, email=user.email)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
async def read_me(user: User = Depends(get_current_user)):
    return UserOut(id=str(user.id), email=user.email, is_active=user.is_active)
