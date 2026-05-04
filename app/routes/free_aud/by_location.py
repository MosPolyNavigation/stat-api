from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.database import get_db
from app.handlers.filter import filter_svobodn
from app.helpers.svobodn import auditory_is_empty
from app.models import Corpus, Location, Plan, Type
from app.models.nav.auditory import Auditory
from app.schemas import Status
from app.schemas.filter import FilterSvobodnByLocation
from app.schemas.rasp.schedule import ScheduleOut
from app.state import AppState


def register_endpoint(router: APIRouter):
    @router.get(
        "/by-loc",
        response_model=ScheduleOut | Status,
        tags=["free-aud"]
    )
    async def by_loc(
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db),
        filter_: FilterSvobodnByLocation = Depends()
    ):
        state: AppState = request.app.state.app_state
        if state._rasp_lock.locked():
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        schedule = filter_svobodn(state.global_rasp, filter_)
        auditories = (await db.execute(
            Select(Auditory.id_sys)
            .join(Auditory.plans)
            .join(Plan.corpus)
            .join(Corpus.locations)
            .filter(Location.id_sys == filter_.loc_id)
            .join(Auditory.typ)
            .filter(Type.name.in_(
                ["Лаборатория",
                 "Учебная аудитория",
                 "Пока не известно",
                 "Клуб / секция / внеучебка"]))
        )).scalars().all()

        return auditory_is_empty(schedule, list(auditories), filter_)
