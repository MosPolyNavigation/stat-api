"""CRUD-эндпоинты просмотра пользователей."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from typing import Union
from app.database import get_db
from app.models.auth.user import User
from app.schemas.user import UserOut
from app.helpers.permissions import require_rights
from app.routes.get.generate_resp import generate_resp


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинты чтения пользователей (список и конкретный пользователь).

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленными обработчиками.
    """

    @router.get(
        "",
        description="Получение списка пользователей с пагинацией",
        response_model=Page[UserOut],
        dependencies=[Depends(require_rights("users", "view"))],
        responses=generate_resp(Page[UserOut])
    )
    async def read_users(db: AsyncSession = Depends(get_db)) -> Page[UserOut]:
        """
        Возвращает список пользователей с пагинацией.

        Args:
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Page[UserOut]: Страница результатов с пользователями.
        """
        return await apaginate(db, Select(User))

    @router.get(
        "/{user_id}",
        description="Получение данных конкретного пользователя",
        response_model=UserOut,
        dependencies=[Depends(require_rights("users", "view"))],
    )
    async def read_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserOut:
        """
        Возвращает пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            UserOut: Найденный пользователь.
        """
        user: Union[User, None] = (await db.execute(Select(User).filter(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден"
            )

        return UserOut(
            id=user.id,
            login=user.login,
            is_active=user.is_active
        )

    return router
