from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app.database import get_db
from app.models.auth.user import User
from app.schemas.user import UserOut
from app.helpers.permissions import require_rights

password_hash = PasswordHash.recommended()


def register_endpoint(router: APIRouter):
    "Эндпоинт для изменения данных пользователя"

    @router.patch(
        "/{user_id}",
        description="Редактирование пользователя (смена пароля или статуса)",
        dependencies=[Depends(require_rights("users", "edit"))]
    )
    async def update_user(
        user_id: int,
        password: str | None = Form(None, description="Новый пароль"),
        is_active: bool | None = Form(None, description="Активен ли пользователь"),
        db: Session = Depends(get_db)
    ):
        # Проверяем, существует ли пользователь
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Флаги изменений
        changes = []

        # Обновляем данные
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

        db.commit()
        db.refresh(user)

        # Формируем сообщение об успешных изменениях
        message = f"Успешно изменены поля: {', '.join(changes)}"

        return {
            "message": message,
            "user": UserOut(
                id=user.id,
                login=user.login,
                is_active=user.is_active
            )
        }
