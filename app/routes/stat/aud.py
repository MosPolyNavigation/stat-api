"""Сбор статистики выбора аудиторий."""

from fastapi import APIRouter, Depends, Body, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import Status, SelectedAuditoryIn
from app.handlers import check_user, insert_aud_selection


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/select-aud` (Swagger tag `stat`) для фиксации выбора аудитории.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.put(
        "/select-aud",
        description="Эндпоинт для добавления выбора аудитории",
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
            },
            429: {
                'model': Status,
                "description": "Too many requests",
                'content': {
                    "application/json": {
                        "example": {
                            "status":
                                "Too many requests for this user within one second"
                        }
                    }
                }
            }
        }
    )
    async def add_selected_aud(
            request: Request,
            response: Response,
            data: SelectedAuditoryIn = Body(),
            db: AsyncSession = Depends(get_db),
    ):
        """
        Добавляет выбор аудитории и защищает от частых повторных запросов.

        Args:
            request: Текущий Request от FastAPI.
            response: Объект Response для задания статуса.
            data: Данные выбранной аудитории.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Status: Статус добавления записи.
        """
        state = request.app.state
        if check_user(state, data.user_id) < 1:
            response.status_code = 429
            return Status(
                status="Too many requests for this user within one second"
            )
        return await insert_aud_selection(db, data)

    return router
