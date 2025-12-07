"""Маршрут фиксации выбора аудитории пользователем."""

from fastapi import APIRouter, Body, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import check_user, insert_aud_selection
from app.schemas import SelectedAuditoryIn, Status


def register_endpoint(router: APIRouter):
    """Регистрирует PUT `/select-aud`."""

    @router.put(
        "/select-aud",
        description="Сохраняет выбор аудитории и результат построения маршрута.",
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
            429: {
                "model": Status,
                "description": "Too many requests",
                "content": {
                    "application/json": {
                        "example": {"status": "Too many requests for this user within one second"}
                    }
                },
            },
        },
    )
    async def add_selected_aud(
        request: Request,
        response: Response,
        data: SelectedAuditoryIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        """Добавляет запись выбора аудитории с ограничением по частоте запросов."""
        state = request.app.state
        if check_user(state, data.user_id) < 1:
            response.status_code = 429
            return Status(status="Too many requests for this user within one second")
        return await insert_aud_selection(db, data)
