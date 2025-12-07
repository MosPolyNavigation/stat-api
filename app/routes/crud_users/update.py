"""Обновление учетных записей пользователей."""

from typing import Union

from fastapi import APIRouter, Depends, Form, HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.user import User
from app.schemas.user import UserOut, UserUpdateResponse

password_hash = PasswordHash.recommended()


def register_endpoint(router: APIRouter):
    """Регистрирует PATCH обновления пользователя."""

    @router.patch(
        "/{user_id}",
        description="Частично обновляет данные пользователя (пароль, статус).",
        response_model=UserUpdateResponse,
        dependencies=[Depends(require_rights("users", "edit"))],
    )
    async def update_user(
        user_id: int,
        password: str | None = Form(None, description="Новый пароль"),
        is_active: bool | None = Form(None, description="Активен ли пользователь"),
        db: AsyncSession = Depends(get_db),
    ):
        """Обновляет пароль и/или статус пользователя."""
        user: Union[User, None] = (await db.execute(Select(User).filter(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        changes = []

        if password:
            user.hash = password_hash.hash(password)
            changes.append("пароль")

        if is_active is not None and is_active != user.is_active:
            user.is_active = is_active
            changes.append("статус")

        if not changes:
            return UserUpdateResponse(
                message="Изменений нет",
                user=UserOut(id=user.id, login=user.login, is_active=user.is_active),
            )

        await db.commit()
        await db.refresh(user)

        message = f"Изменены поля: {', '.join(changes)}"

        return UserUpdateResponse(
            message=message,
            user=UserOut(id=user.id, login=user.login, is_active=user.is_active),
        )
