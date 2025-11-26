from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from app.database import get_db
from app.handlers.filter import filter_svobodn
from app.helpers.svobodn import auditory_is_empty
from app.models import Plan, Corpus, Type
from app.schemas import Status
from app.schemas.filter import FilterSvobodnByCorpus
from app.schemas.rasp.schedule import ScheduleOut
from app.models.nav.auditory import Auditory
import app.globals as globals_


def register_endpoint(router: APIRouter):
    @router.get(
        "/by-corpus",
        response_model=ScheduleOut | Status,
        tags=["free-aud"]
    )
    async def by_corpus(
        response: Response,
        db: AsyncSession = Depends(get_db),
        filter_: FilterSvobodnByCorpus = Depends()
    ):
        if globals_.locker:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        schedule = filter_svobodn(globals_.global_rasp, filter_)
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
