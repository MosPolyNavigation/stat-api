"""Маршрут сохранения смены плана этажа пользователем."""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import insert_changed_plan
from app.schemas import ChangePlanIn, Status


def register_endpoint(router: APIRouter):
    """Регистрирует PUT `/change-plan`."""

    @router.put(
        "/change-plan",
        description="Сохраняет факт переключения на другой план.",
        response_model=Status,
        tags=["stat"],
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
                "description": "Status of adding new object to db",
            },
        },
    )
    async def add_changed_plan(
        data: ChangePlanIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        """Добавляет запись смены плана в статистику."""
        return await insert_changed_plan(db, data)
