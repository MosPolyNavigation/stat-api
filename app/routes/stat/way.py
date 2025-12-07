"""Маршрут фиксации начала пути пользователя."""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import insert_start_way
from app.schemas import StartWayIn, Status


def register_endpoint(router: APIRouter):
    """Регистрирует PUT `/start-way`."""

    @router.put(
        "/start-way",
        description="Сохраняет попытку построения пути между аудиториями.",
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
    async def add_started_way(
        data: StartWayIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        """Добавляет запись о старте маршрута в статистику."""
        return await insert_start_way(db, data)
