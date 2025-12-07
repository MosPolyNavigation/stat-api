"""Ручки авторизации и получения профиля текущего пользователя."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.auth_utils import get_current_active_user
from app.models.auth.user import User
from app.schemas import UserOut

# Хешер паролей (использует безопасные настройки по умолчанию).
password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class Token(BaseModel):
    """Модель access-токена для ответа авторизации."""

    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, что пароль совпадает с хешем в базе."""
    return password_hash.verify(plain_password, hashed_password)


async def get_user_by_login(db: AsyncSession, login: str) -> Optional[User]:
    """Возвращает пользователя по логину или None."""
    return (await db.execute(select(User).filter_by(login=login))).scalar()


async def authenticate_user(db: AsyncSession, login: str, password: str) -> Optional[User]:
    """Проверяет логин/пароль и возвращает пользователя при успехе."""
    user = await get_user_by_login(db, login)
    if not user or not verify_password(password, user.hash):
        return None
    return user


async def create_token(user: User, db: AsyncSession) -> str:
    """Создает и сохраняет новый токен для пользователя."""
    token = str(uuid.uuid4())
    user.token = token
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return token


def register_endpoint(router: APIRouter):
    """Регистрирует ручки `/token` и `/me`."""

    @router.post(
        "/token",
        description="Выдает bearer-токен по паре логин/пароль.",
        response_model=Token,
        tags=["auth"],
    )
    async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_db),
    ):
        """Возвращает access_token или 400 при неверных данных."""
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Неверный логин или пароль")

        access_token = await create_token(user, db)
        return Token(access_token=access_token, token_type="bearer")

    @router.get(
        "/me",
        description="Возвращает данные текущего пользователя.",
        response_model=UserOut,
        tags=["auth"],
    )
    async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: AsyncSession = Depends(get_db),
    ):
        """Обновляет пользователя из БД и возвращает его данные и права."""
        await db.refresh(current_user)
        result = UserOut(id=current_user.id, login=current_user.login, is_active=current_user.is_active)
        result.rights_by_goals = await current_user.get_rights(db)
        return result
