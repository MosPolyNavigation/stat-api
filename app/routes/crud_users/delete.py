from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.helpers.permissions import require_rights


def register_endpoint(router: APIRouter):
    "Эндпоинт для удаления пользователя"

    @router.delete(
        "/{user_id}",
        description="Удаление пользователя",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("users", "delete"))]
    )
    async def delete_user(user_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        db.delete(user)
        db.commit()

        return {
            "message": f"Пользователь с ID {user_id} успешно удалён",
            "user_id": user_id
        }
