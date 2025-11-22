from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy import Select
from sqlalchemy.orm import Session
from typing import Union

from app.database import get_db
from app.models.auth.user import User
from app.helpers.permissions import require_rights
from app.helpers.auth_utils import get_current_user
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
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        # Проверяем связь user-role
        existing: Union[UserRole, None] = db.execute(
            Select(UserRole).filter_by(user_id=user_id, role_id=role_id)
        ).scalar_one_or_none()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="У пользователя нет такой роли"
            )

        db.delete(existing)
        db.commit()

        return {
            "message": "Роль успешно удалена у пользователя",
            "user_id": user_id,
            "role_id": role_id
        }
