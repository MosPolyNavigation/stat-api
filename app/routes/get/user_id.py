from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.handlers import create_user_id
from app.schemas import UserId, Status


def register_endpoint(router: APIRouter):
    @router.get(
        "/user-id",
        description="Эндпоинт для получения уникального id пользователя",
        response_model=UserId,
        tags=["get"],
        responses={
            500: {
                'model': Status,
                'description': "Server side error",
                'content': {
                    "application/json": {
                        "example": {"status": "Some error"}
                    }
                }
            },
            200: {
                'model': UserId,
                "description": "Newly generated user_id"
            }
        }
    )
    async def get_uuid(db: Session = Depends(get_db)):
        """
        Эндпоинт для получения уникального идентификатора пользователя.

        Этот эндпоинт возвращает новый уникальный идентификатор пользователя.

        Args:
            db: Сессия базы данных.

        Returns:
            UserId: Новый уникальный идентификатор пользователя.
        """
        return await create_user_id(db)
