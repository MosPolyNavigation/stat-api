from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app.database import get_db
from app.models.auth.user import User
from app.helpers.permissions import require_rights
from app.schemas.user import UserOut

password_hash = PasswordHash.recommended()


def register_endpoint(router: APIRouter):
    "Эндпоинт для создания нового пользователя"

    @router.post(
        "",
        description="Добавление нового пользователя",
        response_model=UserOut,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_rights("users", "create"))]
    )
    async def create_user(
        login: str = Form(..., description="Логин пользователя"),
        password: str = Form(..., description="Пароль пользователя"),
        is_active: bool = Form(True, description="Активен ли пользователь"),
        db: Session = Depends(get_db)
    ):
        # Проверяем, существует ли пользователь
        existing = db.query(User).filter(User.login == login).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким логином уже существует"
            )

        # Создаем нового пользователя
        new_user = User(
            login=login,
            hash=password_hash.hash(password),
            is_active=is_active
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Возвращаем данные по схеме
        return UserOut(
            login=new_user.login,
            is_active=new_user.is_active
        )
