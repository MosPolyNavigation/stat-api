"""Маршрут проверки существования user_id."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers.check import check_user_id
from app.schemas import Status, UserIdCheck


def register_endpoint(router: APIRouter):
    """Регистрирует ручку `/user-id` для проверки user_id."""

    @router.get(
        "/user-id",
        description="Проверяет наличие user_id в базе.",
        response_model=Status,
        tags=["check"],
        responses={
            500: {
                "model": Status,
                "description": "Server side error",
                "content": {"application/json": {"example": {"status": "Some error"}}},
            },
            404: {
                "model": Status,
                "description": "Item not found",
                "content": {"application/json": {"example": {"status": "User not found"}}},
            },
            200: {
                "model": Status,
                "description": "User found",
            },
        },
    )
    async def check_uuid(
        data: UserIdCheck = Depends(),
        db: AsyncSession = Depends(get_db),
    ):
        """Возвращает статус 200 если пользователь найден, иначе 404."""
        return await check_user_id(db, data)
