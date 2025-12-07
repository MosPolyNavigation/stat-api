"""Маршрут генерации нового user_id."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import create_user_id
from app.schemas import Status, UserId


def register_endpoint(router: APIRouter):
    """Регистрирует ручку получения нового идентификатора пользователя."""

    @router.get(
        "/user-id",
        description="Генерирует и возвращает новый уникальный user_id.",
        response_model=UserId,
        tags=["get"],
        responses={
            500: {
                "model": Status,
                "description": "Server side error",
                "content": {"application/json": {"example": {"status": "Some error"}}},
            },
            200: {
                "model": UserId,
                "description": "Newly generated user_id",
            },
        },
    )
    async def get_uuid(db: AsyncSession = Depends(get_db)):
        """Создает новый идентификатор пользователя в базе и возвращает его."""
        return await create_user_id(db)
