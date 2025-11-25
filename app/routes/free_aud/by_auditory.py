from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from app.database import get_db
from app.handlers.filter import filter_svobodn
from app.helpers.svobodn import auditory_is_empty
from app.models import Plan
from app.schemas import Status
from app.schemas.filter import FilterSvobodnForAud
from app.schemas.rasp.schedule import Schedule
from app.models.nav.auditory import Auditory
import app.globals as globals_


def register_endpoint(router: APIRouter):
    @router.get(
        "/by-aud",
        response_model=Schedule | Status,
        tags=["free-aud"]
    )
    async def by_plan(
        response: Response,
        filter_: FilterSvobodnForAud = Depends()
    ):
        if globals_.locker:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        schedule = {filter_.aud_id: globals_.global_rasp[filter_.aud_id]}
        schedule = filter_svobodn(schedule, filter_)
        auditories = [filter_.aud_id,]

        return auditory_is_empty(schedule, auditories, filter_)
