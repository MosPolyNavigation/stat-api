import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.nav.plan import Plan
from app.models.nav.location import Location
from app.schemas.nav.plan import PlanNav


def register_endpoint(router: APIRouter):
    """
    Эндпоинт для получения плана:
    /api/nav/plan?plan={plan_id}

    Возвращает JSON формата {loc_id}{plan_id}.json
    """

    @router.get(
        "/plan",
        description="Получение навигационного плана",
        response_model=PlanNav,
    )
    async def get_plan(
        plan: str,
        db: AsyncSession = Depends(get_db),
    ) -> PlanNav:
        #  находим план по id_sys и подгружаем corpus, floor, svg
        stmt = (
            Select(Plan)
            .options(
                selectinload(Plan.corpus),
                selectinload(Plan.floor),
                selectinload(Plan.svg),
            )
            .filter(Plan.id_sys == plan)
        )

        plan_obj: Plan | None = (
            await db.execute(stmt)
        ).scalar_one_or_none()

        if plan_obj is None:
            raise HTTPException(status_code=404, detail="Plan not found" )

        # Находим кампус по loc_id корпуса
        location: Location | None = (
            await db.execute(
                Select(Location).filter(
                    Location.id == plan_obj.corpus.loc_id
                )
            )
        ).scalar_one_or_none()

        if location is None:
            raise HTTPException(
                status_code=500,
                detail="Локация для корпуса плана не найдена",
            )

        # Разбираем JSON-поля entrances и graph
        try:
            entrances = json.loads(plan_obj.entrances)
        except ValueError:
            entrances = []

        try:
            graph = json.loads(plan_obj.graph)
        except ValueError:
            graph = []

        svg_link: str | None = (
            plan_obj.svg.link if plan_obj.svg is not None else None
        )

        spaces: list = []

        return PlanNav(
            planName=plan_obj.id_sys,
            svgLink=svg_link,
            campus=location.id_sys,
            corpus=plan_obj.corpus.id_sys,
            floor=plan_obj.floor.name,
            entrances=entrances,
            graph=graph,
            spaces=spaces,
        )
