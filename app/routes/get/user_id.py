"""Эндпоинт для выдачи нового user_id."""

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.handlers import create_user_id
from app.schemas import UserId, Status


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/user-id` (Swagger tag `get`) для генерации user_id.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

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
    async def get_uuid(db: AsyncSession = Depends(get_db)):
        """
        Эндпоинт для получения уникального идентификатора пользователя.

        Args:
            db: Сессия базы данных.

        Returns:
            UserId: Новый уникальный идентификатор пользователя.
        """
        return await create_user_id(db)

    return router
