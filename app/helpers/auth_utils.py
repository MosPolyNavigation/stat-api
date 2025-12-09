"""Вспомогательные зависимости для авторизации OAuth2 и проверки прав."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Annotated
from app.database import get_db
from app.models.auth.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает пользователя по токену из заголовка Authorization.

    Args:
        token: Значение Bearer-токена.
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        User: Найденный пользователь.
    """
    user = (await db.execute(Select(User).filter(User.token == token))).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации недействителен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_user_with_loaded_fields(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает пользователя по токену и подгружает связанные роли.

    Args:
        token: Значение Bearer-токена.
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        User: Пользователь с загруженными связями user_roles.
    """
    user = (await db.execute(
        Select(User).filter(User.token == token)
        .options(selectinload(User.user_roles))
    )).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации недействителен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Убеждается, что пользователь активирован, иначе возвращает 400.

    Args:
        current_user: Пользователь, полученный через зависимость get_current_user.

    Returns:
        User: Активный пользователь.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Пользователь не активен")
    return current_user
