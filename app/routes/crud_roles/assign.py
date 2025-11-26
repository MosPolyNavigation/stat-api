from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from app.database import get_db
from app.helpers.permissions import require_rights
from app.helpers.auth_utils import get_current_user
from app.models.auth.user import User
from app.models.auth.role import Role
from app.models.auth.user_role import UserRole


def register_endpoint(router: APIRouter):
    """
    Эндпоинт для привязки роли к пользователю
    """

    @router.post(
        "/assign",
        description="Назначение роли пользователю",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("roles", "grant"))]
    )
    async def assign_role(
        user_id: int = Form(...),
        role_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):

        # Проверяем, существует ли пользователь
        user: Union[User, None] = (await db.execute(
            Select(User).filter_by(id=user_id)
        )).scalar_one_or_none()

        if not user:
            raise HTTPException(404, "Пользователь не найден")

        # Проверяем, существует ли роль
        role: Union[Role, None] = (await db.execute(
            Select(Role).filter_by(id=role_id)
        )).scalar_one_or_none()

        if not role:
            raise HTTPException(404, "Роль не найдена")

        # Проверяем, есть ли уже такая привязка
        existing: Union[UserRole, None] = (await db.execute(
            Select(UserRole).filter_by(user_id=user_id, role_id=role_id)
        )).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="У пользователя уже есть эта роль"
            )

        # Добавляем новую связь
        db.add(UserRole(user_id=user_id, role_id=role_id))
        await db.commit()

        return {
            "message": "Роль успешно назначена пользователю",
            "user_id": user_id,
            "role_id": role_id
        }
