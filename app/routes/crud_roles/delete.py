"""Удаление ролей."""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.role import Role
from app.schemas.role import RoleActionResponse


def register_endpoint(router: APIRouter):
    """Регистрирует DELETE удаления роли."""

    @router.delete(
        "/{role_id}",
        description="Удаляет роль по ID.",
        status_code=status.HTTP_200_OK,
        response_model=RoleActionResponse,
        dependencies=[Depends(require_rights("roles", "delete"))],
    )
    async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
        """Удаляет роль из базы или возвращает 404."""
        role: Union[Role, None] = (await db.execute(Select(Role).filter(Role.id == role_id))).scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")

        await db.delete(role)
        await db.commit()
        return RoleActionResponse(message=f"Роль с ID {role_id} удалена", role_id=role_id)
