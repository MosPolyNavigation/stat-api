"""Сбор статистики построения маршрутов."""

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import insert_start_way
from app.schemas import StartWayIn, Status


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/start-way` (Swagger tag `stat`).

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.put(
        "/start-way",
        description="Эндпоинт для добавления начатого пути",
        response_model=Status,
        tags=["stat"],
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
                'description': "Item not found",
                'content': {
                    "application/json": {
                        "example": {"status": "User not found"}
                    }
                }
            },
            200: {
                'model': Status,
                "description": "Status of adding new object to db"
            }
        }
    )
    async def add_started_way(
            data: StartWayIn = Body(),
            db: AsyncSession = Depends(get_db)
    ):
        """
        Добавляет запись о начале построения маршрута.

        Args:
            data: Данные начатого пути.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Status: Статус добавления нового объекта в базу данных.
        """
        return await insert_start_way(db, data)

    return router
