"""Создание пользователей."""

from typing import Union

from fastapi import APIRouter, Depends, Form, HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.user import User
from app.schemas.user import UserOut

password_hash = PasswordHash.recommended()


def register_endpoint(router: APIRouter):
    """Регистрирует POST создания пользователя."""

    @router.post(
        "",
        description="Создает нового пользователя.",
        response_model=UserOut,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_rights("users", "create"))],
    )
    async def create_user(
        login: str = Form(..., description="Логин пользователя"),
        password: str = Form(..., description="Пароль пользователя"),
        is_active: bool = Form(True, description="Активен ли пользователь"),
        db: AsyncSession = Depends(get_db),
    ):
        """Создает пользователя, если логин свободен."""
        existing: Union[User, None] = (await db.execute(Select(User).filter(User.login == login))).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким логином уже существует",
            )

        new_user = User(
            login=login,
            hash=password_hash.hash(password),
            is_active=is_active,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserOut(id=new_user.id, login=new_user.login, is_active=new_user.is_active)
