from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.handlers import insert_tg_event
from app.schemas import Status, TgBotEventIn


def register_endpoint(router: APIRouter):
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
            404: {
                'model': Status,
                'description': "Объект не найден",
                'content': {
                    "application/json": {
                        "example": {"status": "Не найдено"}
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
        Приём события телеграм-бота.

        Создаёт пользователя и тип события при их отсутствии,
        затем сохраняет событие с привязками и меткой времени.

        Args:
            data: Данные события;
            db: Сессия базы данных.

        Returns:
            Status: Результат операции.
        """
        return await insert_tg_event(db, data)
