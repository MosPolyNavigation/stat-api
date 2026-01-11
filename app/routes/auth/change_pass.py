from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Form, Header, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash

from app.database import get_db
from app.models.auth.user import User
from app.helpers.auth_utils import get_current_user

password_hash = PasswordHash.recommended()


def register_endpoint(router: APIRouter):
    "Эндпоинт для смены собственного пароля"

    @router.post(
        "/change-pass",
        description="Смена пароля текущего пользователя",
        tags=["auth"],
        status_code=status.HTTP_200_OK,
    )
    async def change_own_password(
        old_password: str = Form(...),
        new_password: str = Form(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):

        if not password_hash.verify(old_password, current_user.hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль",
            )

        current_user.hash = password_hash.hash(new_password)
        await db.commit()

        return {"message": "Пароль успешно изменён"}
