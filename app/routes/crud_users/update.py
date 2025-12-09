"""CRUD-эндпоинт для обновления данных пользователя."""

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
    """
    Регистрирует эндпоинт частичного обновления пользователя.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.patch(
        "/{user_id}",
        description="Редактирование пользователя (смена пароля или статуса)",
        dependencies=[Depends(require_rights("users", "edit"))]
    )
    async def update_user(
        user_id: int,
        password: str | None = Form(None, description="Новый пароль"),
        is_active: bool | None = Form(None, description="Активен ли пользователь"),
        db: AsyncSession = Depends(get_db)
    ):
        """
        Обновляет пароль и/или статус пользователя.

        Args:
            user_id: Идентификатор пользователя.
            password: Новый пароль, если требуется изменить.
            is_active: Новый статус активности.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            dict: Сообщение и актуальные данные пользователя.
        """
        user: Union[User, None] = (await db.execute(Select(User).filter(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        changes = []

        if password:
            user.hash = password_hash.hash(password)
            changes.append("пароль")

        if is_active is not None and is_active != user.is_active:
            user.is_active = is_active
            changes.append("статус")

        if not changes:
            return {
                "message": "Изменений не было",
                "user": UserOut(
                    id=user.id,
                    login=user.login,
                    is_active=user.is_active
                )
            }

        await db.commit()
        await db.refresh(user)

        message = f"Успешно изменены поля: {', '.join(changes)}"

        return {
            "message": message,
            "user": UserOut(
                id=user.id,
                login=user.login,
                is_active=user.is_active
            )
        }

    return router
