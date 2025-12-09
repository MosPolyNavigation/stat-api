"""Сбор статистики смены планов навигации."""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import insert_changed_plan
from app.schemas import ChangePlanIn, Status


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/change-plan` (Swagger tag `stat`).

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.put(
        "/change-plan",
        description="Эндпоинт для добавления смены плана",
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
    async def add_changed_plan(
            data: ChangePlanIn = Body(),
            db: AsyncSession = Depends(get_db)
    ):
        """
        Добавляет событие смены плана пользователем.

        Args:
            data: Данные смены плана.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Status: Результат записи.
        """
        return await insert_changed_plan(db, data)

    return router
