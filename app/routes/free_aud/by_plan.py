"""Поиск свободных аудиторий по плану корпуса."""

import app.globals as globals_
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.database import get_db
from app.handlers.filter import filter_svobodn
from app.helpers.svobodn import auditory_is_empty
from app.models import Plan, Type
from app.models.nav.auditory import Auditory
from app.schemas import Status
from app.schemas.filter import FilterSvobodnForPlan
from app.schemas.rasp.schedule import ScheduleOut


def register_endpoint(router: APIRouter):
    """Регистрирует GET `/by-plan`."""

    @router.get(
        "/by-plan",
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
    async def by_plan(
        response: Response,
        db: AsyncSession = Depends(get_db),
        filter_: FilterSvobodnForPlan = Depends(),
    ):
        """Возвращает свободные аудитории для выбранного плана корпуса."""
        if globals_.locker:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        schedule = filter_svobodn(globals_.global_rasp, filter_)
        auditories = (
            await db.execute(
                Select(Auditory.id_sys)
                .join(Auditory.plans)
                .filter(Plan.id_sys == filter_.plan_id)
                .join(Auditory.typ)
                .filter(
                    Type.name.in_(
                        [
                            ">ø+?‘?ø‘'?‘?ñ‘?",
                            "?‘Øç+?ø‘? ø‘??ñ‘'?‘?ñ‘?",
                            "??óø ?ç ñú?ç‘?‘'??",
                            "?>‘?+ / ‘?çó‘Åñ‘? / ??ç‘?‘Øç+óø",
                        ]
                    )
                )
            )
        ).scalars().all()

        return auditory_is_empty(schedule, list(auditories), filter_)
