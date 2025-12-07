"""Чтение пользователей."""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.user import User
from app.routes.get.generate_resp import generate_resp
from app.schemas.user import UserOut


def register_endpoint(router: APIRouter):
    """Регистрирует GET-ручки для получения пользователей."""

    @router.get(
        "",
        description="Возвращает список пользователей постранично.",
        response_model=Page[UserOut],
        dependencies=[Depends(require_rights("users", "view"))],
        responses=generate_resp(Page[UserOut]),
    )
    async def read_users(db: AsyncSession = Depends(get_db)) -> Page[UserOut]:
        """Возвращает пагинированный список пользователей."""
        return await apaginate(db, Select(User))

    @router.get(
        "/{user_id}",
        description="Возвращает пользователя по идентификатору.",
        response_model=UserOut,
        dependencies=[Depends(require_rights("users", "view"))],
    )
    async def read_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserOut:
        """Возвращает пользователя или 404, если не найден."""
        user: Union[User, None] = (await db.execute(Select(User).filter(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден",
            )

        return UserOut(id=user.id, login=user.login, is_active=user.is_active)
