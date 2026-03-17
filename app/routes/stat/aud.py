from fastapi import APIRouter, Depends, Body, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import Status, SelectedAuditoryIn
from app.handlers import check_user, insert_aud_selection
from app.guards.governor import stat_rate_limiter


def register_endpoint(router: APIRouter):
    @router.put(
        "/select-aud",
        description="Эндпоинт для добавления выбора аудитории",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
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
                            "detail":
                                "Too many requests for this user within one second"
                        }
                    }
                }
            }
        }
    )
    async def add_selected_aud(
            data: SelectedAuditoryIn = Body(),
            db: AsyncSession = Depends(get_db),
    ):
        """
        Эндпоинт для добавления выбора аудитории.

        Этот эндпоинт добавляет выбор аудитории в базу данных.

        Args:
            request: Запрос;
            response: Ответ;
            data: Данные выбора аудитории;
            db: Сессия базы данных.

        Returns:
            Status: Статус добавления нового объекта в базу данных.
        """
        return await insert_aud_selection(db, data)
