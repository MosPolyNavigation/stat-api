"""Сбор статистики событий телеграм-бота."""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.handlers import insert_tg_event
from app.schemas import Status, TgBotEventIn


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/tg-bot` (Swagger tag `stat`) для записи событий бота.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.put(
        "/tg-bot",
        description="Эндпоинт для записи событий телеграм-бота",
        response_model=Status,
        tags=["stat"],
        responses={
            500: {
                'model': Status,
                'description': "Ошибка на стороне сервера",
                'content': {
                    "application/json": {
                        "example": {"status": "Произошла ошибка"}
                    }
                }
            },
            200: {
                'model': Status,
                "description": "Статус добавления записи в базу"
            }
        }
    )
    async def add_tg_event(
        data: TgBotEventIn = Body(),
        db: AsyncSession = Depends(get_db)
    ):
        """
        Принимает событие телеграм-бота и сохраняет его.

        Args:
            data: Данные события.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Status: Результат операции.
        """
        return await insert_tg_event(db, data)

    return router
