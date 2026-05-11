from typing import Annotated
from fastapi import APIRouter, Request, Response
from fastapi.params import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers.filter import filter_svobodn
from app.helpers.svobodn import auditory_is_empty
from app.models import Corpus, Plan, Type, Auditory
from app.schemas import Status
from app.schemas.filter import FilterSvobodnByCorpus
from app.schemas.rasp.schedule import ScheduleOut
from app.state import AppState


def register_endpoint(router: APIRouter):
    @router.get(
        "/by-corpus",
        response_model=ScheduleOut | Status,
        tags=["free-aud"]
    )
    async def by_corpus(
        request: Request,
        response: Response,
        db: Annotated[AsyncSession, Depends(get_db)],
        filter_: Annotated[FilterSvobodnByCorpus, Depends()]
    ):
        state: AppState = request.app.state.app_state
        if state.rasp_lock.locked() or state.global_rasp is None:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        schedule = filter_svobodn(state.global_rasp, filter_)
        auditories = (await db.execute(
            Select(Auditory.id_sys)
            .join(Auditory.plans)
            .join(Plan.corpus)
            .filter(Corpus.id_sys == filter_.corpus_id)
            .join(Auditory.typ)
            .filter(Type.name.in_(
                ["Лаборатория",
                 "Учебная аудитория",
                 "Пока не известно",
                 "Клуб / секция / внеучебка"]))
        )).scalars().all()

        return auditory_is_empty(schedule, list(auditories), filter_)
