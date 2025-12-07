"""Назначение ролей пользователям."""

from typing import Union

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.auth_utils import get_current_user
from app.helpers.permissions import require_rights
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.auth.user_role import UserRole
from app.schemas.role import RoleAssignmentResponse


def register_endpoint(router: APIRouter):
    """Регистрирует POST для привязки роли."""

    @router.post(
        "/assign",
        description="Назначает роль пользователю.",
        status_code=status.HTTP_200_OK,
        response_model=RoleAssignmentResponse,
        dependencies=[Depends(require_rights("roles", "grant"))],
    )
    async def assign_role(
        user_id: int = Form(...),
        role_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Добавляет связь user-role, если она еще не существует."""
        user: Union[User, None] = (await db.execute(Select(User).filter_by(id=user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(404, "Пользователь не найден")

        role: Union[Role, None] = (await db.execute(Select(Role).filter_by(id=role_id))).scalar_one_or_none()
        if not role:
            raise HTTPException(404, "Роль не найдена")

        existing: Union[UserRole, None] = (
            await db.execute(Select(UserRole).filter_by(user_id=user_id, role_id=role_id))
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="У пользователя уже есть эта роль",
            )

        db.add(UserRole(user_id=user_id, role_id=role_id))
        await db.commit()

        return RoleAssignmentResponse(
            message="Роль успешно назначена пользователю",
            user_id=user_id,
            role_id=role_id,
        )
