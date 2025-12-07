"""Маршрут получения расписания по аудитории или целиком."""

from typing import Union

from fastapi import APIRouter
from starlette.responses import Response

import app.globals as globals_
from app.schemas import Status
from app.schemas.rasp.schedule import Auditory, Schedule


def register_endpoint(router: APIRouter):
    """Регистрирует ручку `/schedule`."""

    @router.get(
        "/schedule",
        tags=["get"],
        response_model=Union[Schedule, Auditory, Status],
        responses={
            404: {
                "model": Status,
                "description": "Нет расписания для аудитории",
                "content": {"application/json": {"example": {"status": "No schedule for specified auditory"}}},
            },
            425: {
                "model": Status,
                "description": "Расписание еще не загружено",
                "content": {
                    "application/json": {
                        "example": {"status": "Schedule is not loaded yet. Try again later"}
                    }
                },
            },
        },
    )
    async def get_schedule(
        response: Response,
        auditory: Union[str, None] = None,
    ):
        """Возвращает расписание по конкретной аудитории или весь кеш."""
        if not globals_.global_rasp:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        if not auditory:
            return globals_.global_rasp
        aud_schedule = globals_.global_rasp[auditory]
        if aud_schedule:
            return aud_schedule
        response.status_code = 404
        return Status(status="No schedule for specified auditory")
