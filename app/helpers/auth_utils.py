from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.constants import GOAL_RIGHTS
from app.database import get_db
from app.models import User
from app.helpers.token_utils import (
    decode_access_token,
    normalize_token_error,
    validate_access_payload,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# Получает пользователя по Access JWT
async def get_user_by_access_token(token: str, db: AsyncSession) -> User | None:
    payload = decode_access_token(token)
    user_id = validate_access_payload(payload)
    return (
        await db.execute(select(User).filter(User.id == user_id))
    ).scalar_one_or_none()


# Получает пользователя по старому токену из БД
async def get_user_by_legacy_token(token: str, db: AsyncSession) -> User | None:
    return (
        await db.execute(select(User).filter(User.token == token))
    ).scalar_one_or_none()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    """Получить пользователя по Access JWT."""
    user: User | None = None
    _ = user

    try:
        # Сначала пытаемся найти пользователя по новому Access JWT
        user = await get_user_by_access_token(token, db)
    except Exception as exc:
        # Если JWT невалиден, пробуем старый формат токена для совместимости
        user = await get_user_by_legacy_token(token, db)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=normalize_token_error(exc),
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Проверить, активен ли пользователь"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user


def get_goal_rights_map() -> dict[int, list[int]]:
    """
    Формирует маппинг {goal_id: [right_ids]} из константы GOAL_RIGHTS.

    Returns:
        dict[int, list[int]]: маппинг целей к списку допустимых прав
    """

    result: dict[int, list[int]] = {}
    for goal_id, right_id in GOAL_RIGHTS:
        if goal_id not in result:
            result[goal_id] = []
        if right_id not in result[goal_id]:  # на случай дублей в константе
            result[goal_id].append(right_id)

    # Сортируем права по возрастанию для консистентности ответа
    for goal_id in result:
        result[goal_id].sort()

    return result
