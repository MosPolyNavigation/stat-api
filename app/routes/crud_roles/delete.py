"""CRUD-эндпоинт для удаления роли."""

from sqlalchemy.orm import selectinload
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.role import Role


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт удаления роли.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.delete(
        "/{role_id}",
        description="Удаление роли",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("roles", "delete"))]
    )
    async def delete_role(
        role_id: int,
        db: AsyncSession = Depends(get_db)
    ):
        """
        Удаляет роль, если она не назначена пользователям.

        Args:
            role_id: Идентификатор роли.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            dict: Сообщение об удалении роли.
        """
        role: Union[Role, None] = (await db.execute(
            Select(Role).filter(Role.id == role_id)
            .options(selectinload(Role.user_roles))
        )).scalar_one_or_none()
        if not role:
            raise HTTPException(404, "Роль не найдена")

        if role.user_roles:
            raise HTTPException(
                status_code=400,
                detail="Нельзя удалить роль, пока она назначена пользователям"
            )

        await db.delete(role)
        await db.commit()

        return {"message": f"Роль {role_id} удалена", "role_id": role_id}

    return router
