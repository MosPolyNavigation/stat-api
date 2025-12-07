"""Поиск свободной аудитории по ее идентификатору."""

import app.globals as globals_
from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import Response

from app.handlers.filter import filter_svobodn
from app.helpers.svobodn import auditory_is_empty
from app.schemas import Status
from app.schemas.filter import FilterSvobodnForAud
from app.schemas.rasp.schedule import ScheduleOut


def register_endpoint(router: APIRouter):
    """Регистрирует GET `/by-aud`."""

    @router.get(
        "/by-aud",
        response_model=ScheduleOut | Status,
        tags=["free-aud"],
        responses={
            425: {
                "model": Status,
                "description": "Расписание не загружено",
                "content": {
                    "application/json": {
                        "example": {"status": "Schedule is not loaded yet. Try again later"}
                    }
                },
            }
        },
    )
    async def by_aud(
        response: Response,
        filter_: FilterSvobodnForAud = Depends(),
    ):
        """Возвращает информацию о свободности конкретной аудитории."""
        if globals_.locker:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        schedule = {filter_.aud_id: globals_.global_rasp[filter_.aud_id]}
        schedule = filter_svobodn(schedule, filter_)
        auditories = [
            filter_.aud_id,
        ]

        return auditory_is_empty(schedule, auditories, filter_)
