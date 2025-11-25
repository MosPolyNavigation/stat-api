from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.user_role import UserRole


def register_endpoint(router: APIRouter):
    """
    Эндпоинт для удаления роли у пользователя
    """

    @router.post(
        "/unassign",
        description="Удаление роли у пользователя",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("roles", "grant"))]
    )
    async def unassign_role(
        user_id: int = Form(...),
        role_id: int = Form(...),
        db: AsyncSession = Depends(get_db)
    ):
        # Проверяем связь user-role
        existing: Union[UserRole, None] = (await db.execute(
            Select(UserRole).filter_by(user_id=user_id, role_id=role_id)
        )).scalar_one_or_none()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="У пользователя нет такой роли"
            )

        await db.delete(existing)
        await db.commit()

        return {
            "message": "Роль успешно удалена у пользователя",
            "user_id": user_id,
            "role_id": role_id
        }
