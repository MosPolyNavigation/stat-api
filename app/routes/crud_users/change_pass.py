from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash

from app.database import get_db
from app.models.auth.user import User
from app.schemas.user import UserOut
from app.helpers.permissions import require_rights

password_hash = PasswordHash.recommended()


def register_endpoint(router: APIRouter):
    "Эндпоинт для изменения пароля чужого пользователя"

    @router.post(
        "/{user_id}/change-pass",
        description="Смена пароля чужого пользователя",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("users", "edit"))],
    )
    async def change_user_password(
        user_id: int,
        new_password: str = Form(...),
        db: AsyncSession = Depends(get_db),
    ):
        user: Union[User, None] = (
            await db.execute(
                Select(User).filter(User.id == user_id)
            )
        ).scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        user.hash = password_hash.hash(new_password)
        await db.commit()

        return {
            "message": "Пароль пользователя успешно изменён",
            "user_id": user_id,
        }
