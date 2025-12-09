"""Эндпоинт поиска свободных аудиторий по плану этажа."""

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from app.database import get_db
from app.handlers.filter import filter_svobodn
from app.helpers.svobodn import auditory_is_empty
from app.models import Plan, Type
from app.schemas import Status
from app.schemas.filter import FilterSvobodnForPlan
from app.schemas.rasp.schedule import ScheduleOut
from app.models.nav.auditory import Auditory
import app.globals as globals_


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/by-plan` (Swagger tag `free-aud`).

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.get(
        "/by-plan",
        response_model=ScheduleOut | Status,
        tags=["free-aud"]
    )
    async def by_plan(
        response: Response,
        db: AsyncSession = Depends(get_db),
        filter_: FilterSvobodnForPlan = Depends()
    ):
        """
        Возвращает свободные аудитории для выбранного плана этажа.

        Args:
            response: Объект Response для управления статусом.
            db: Асинхронная сессия SQLAlchemy.
            filter_: Параметры фильтрации (план, день, пара).

        Returns:
            ScheduleOut | Status: Свободные аудитории либо описание ошибки загрузки расписания.
        """
        if globals_.locker:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        schedule = filter_svobodn(globals_.global_rasp, filter_)
        auditories = (await db.execute(
            Select(Auditory.id_sys)
            .join(Auditory.plans)
            .filter(Plan.id_sys == filter_.plan_id)
            .join(Auditory.typ)
            .filter(Type.name.in_(
                ["Лаборатория",
                 "Учебная аудитория",
                 "Пока не известно",
                 "Клуб / секция / внеучебка"]))
        )).scalars().all()

        return auditory_is_empty(schedule, list(auditories), filter_)

    return router
