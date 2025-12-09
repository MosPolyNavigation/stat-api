"""Эндпоинты аутентификации OAuth2 и выдачи токенов."""

import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash
from pydantic import BaseModel
from app.database import get_db
from app.models.auth.user import User
from app.helpers.auth_utils import get_current_active_user
from app.schemas import UserOut

# Будет использоваться рекомендуемый алгоритм хэширования паролей
password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class Token(BaseModel):
    """Схема ответа при выдаче токена."""

    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие введенного пароля сохраненному хэшу.

    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хэш, сохраненный в базе.

    Returns:
        bool: True, если пароль корректен.
    """
    return password_hash.verify(plain_password, hashed_password)


async def get_user_by_login(db: AsyncSession, login: str) -> Optional[User]:
    """
    Возвращает пользователя по логину.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        login: Логин пользователя.

    Returns:
        Optional[User]: Найденный пользователь или None.
    """
    return (await db.execute(select(User).filter_by(login=login))).scalar()


async def authenticate_user(db: AsyncSession, login: str, password: str) -> Optional[User]:
    """
    Проверяет существование пользователя и валидность пароля.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        login: Логин пользователя.
        password: Пароль в открытом виде.

    Returns:
        Optional[User]: Пользователь при успешной проверке или None.
    """
    user = await get_user_by_login(db, login)
    if not user or not verify_password(password, user.hash):
        return None
    return user


async def create_token(user: User, db: AsyncSession) -> str:
    """
    Генерирует новый токен (UUID) и сохраняет его у пользователя.

    Args:
        user: Пользователь, которому назначается токен.
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        str: Сгенерированный токен.
    """
    token = str(uuid.uuid4())
    user.token = token
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return token


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинты `/token` и `/me` (Swagger tag `auth`).

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленными обработчиками.
    """

    @router.post(
        "/token",
        description="Эндпоинт для получения токена аутентификации",
        response_model=Token,
        tags=["auth"],
    )
    async def login(
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
            db: AsyncSession = Depends(get_db)
    ):
        """
        Выполняет аутентификацию пользователя и возвращает bearer-токен.

        Args:
            form_data: Форма OAuth2 с логином и паролем.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Token: Сгенерированный токен доступа.
        """
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Некорректный логин или пароль")

        access_token = create_token(user, db)
        return Token(access_token=await access_token, token_type="bearer")

    @router.get(
        "/me",
        description="Эндпоинт для получения данных текущего пользователя по токену",
        response_model=UserOut,
        tags=["auth"],
    )
    async def read_users_me(
            current_user: Annotated[User, Depends(get_current_active_user)],
            db: AsyncSession = Depends(get_db),
    ):
        """
        Возвращает актуальные данные текущего пользователя и его права.

        Args:
            current_user: Авторизованный пользователь.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            UserOut: Данные пользователя и права, отраженные в Swagger.
        """
        await db.refresh(current_user)
        result = UserOut(
            id=current_user.id,
            login=current_user.login,
            is_active=current_user.is_active
        )
        result.rights_by_goals = await current_user.get_rights(db)
        return result

    return router
