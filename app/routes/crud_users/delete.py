"""CRUD-эндпоинт для удаления пользователя."""

from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.auth.user import User
from app.helpers.permissions import require_rights


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт удаления пользователя.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.delete(
        "/{user_id}",
        description="Удаление пользователя",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("users", "delete"))]
    )
    async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
        """
        Удаляет пользователя, кроме администратора с id=1.

        Args:
            user_id: Идентификатор пользователя.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            dict: Сообщение об успешном удалении.
        """

        if user_id == 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя удалить администратора (id=1)",
            )

        user: Union[User, None] = (await db.execute(Select(User).filter(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        await db.delete(user)
        await db.commit()

        return {
            "message": f"Пользователь с ID {user_id} успешно удалён",
            "user_id": user_id
        }

    return router
