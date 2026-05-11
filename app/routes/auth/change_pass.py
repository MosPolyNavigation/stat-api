from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Form, Header, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash

from app.database import get_db
from app.models.auth.user import User
from app.helpers.auth_utils import get_current_user
from app.services.user_logger_service import UserLoggerService, get_user_logger_service

password_hash = PasswordHash.recommended()


def register_endpoint(router: APIRouter):
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
        logger: UserLoggerService = Depends(get_user_logger_service),
    ):
        """Эндпоинт для смены собственного пароля"""
        try:
            if not password_hash.verify(old_password, current_user.hash):
                logger.log(current_user, "Неудачная попытка смены пароля")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверный текущий пароль",
                )

            current_user.hash = password_hash.hash(new_password)
            await db.commit()
            logger.log(current_user, "Запрос смены пароля")
            return {"message": "Пароль успешно изменён"}

        except HTTPException:
            raise

        except Exception:
            logger.log(current_user, "Неудачная попытка смены пароля")
            raise
