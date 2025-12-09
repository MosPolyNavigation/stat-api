"""Эндпоинт проверки существования user_id."""

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import UserIdCheck, Status
from app.handlers.check import check_user_id


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/check/user-id` (Swagger tag `check`).

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.get(
        "/user-id",
        description="Эндпоинт для получения уникального id пользователя",
        response_model=Status,
        tags=["check"],
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
            404: {
                'model': Status,
                'description": "Item not found",
                'content': {
                    "application/json": {
                        "example": {"status": "User not found"}
                    }
                }
            },
            200: {
                'model': Status,
                'description': "User found",
            }
        }
    )
    async def check_uuid(
        data: UserIdCheck = Depends(),
        db: AsyncSession = Depends(get_db)
    ):
        """
        Проверяет существование уникального идентификатора пользователя.

        Args:
            data: Параметры запроса с user_id.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Status: Результат проверки.
        """
        return await check_user_id(db, data)

    return router
