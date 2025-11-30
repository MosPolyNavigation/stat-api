from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.nav.plan import Plan
from app.routes.graphql.permissions import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
    ensure_nav_permission,
)
from .common import get_or_error

DEFAULT_PLAN_ENTRANCES = "[]"
DEFAULT_PLAN_GRAPH = "{}"


@strawberry.type(name="NavPlan")
class NavPlanType:
    id: int
    id_sys: str
    cor_id: int
    floor_id: int
    ready: bool
    entrances: str
    graph: str
    svg_id: Optional[int]
    nearest_entrance: Optional[str]
    nearest_man_wc: Optional[str]
    nearest_woman_wc: Optional[str]
    nearest_shared_wc: Optional[str]


@strawberry.input
class NavPlanInput:
    id_sys: str
    cor_id: int
    floor_id: int
    ready: bool
    nearest_entrance: Optional[str] = None
    nearest_man_wc: Optional[str] = None
    nearest_woman_wc: Optional[str] = None
    nearest_shared_wc: Optional[str] = None


@strawberry.input
class NavPlanUpdateInput:
    id_sys: Optional[str] = None
    cor_id: Optional[int] = None
    floor_id: Optional[int] = None
    ready: Optional[bool] = None
    nearest_entrance: Optional[str] = None
    nearest_man_wc: Optional[str] = None
    nearest_woman_wc: Optional[str] = None
    nearest_shared_wc: Optional[str] = None


def _to_nav_plan(model: Plan) -> NavPlanType:
    return NavPlanType(
        id=model.id,
        id_sys=model.id_sys,
        cor_id=model.cor_id,
        floor_id=model.floor_id,
        ready=model.ready,
        entrances=model.entrances,
        graph=model.graph,
        svg_id=model.svg_id,
        nearest_entrance=model.nearest_entrance,
        nearest_man_wc=model.nearest_man_wc,
        nearest_woman_wc=model.nearest_woman_wc,
        nearest_shared_wc=model.nearest_shared_wc,
    )


async def resolve_nav_plans(
    info: Info,
    id: Optional[int] = None,
    id_sys: Optional[str] = None,
    cor_id: Optional[int] = None,
    floor_id: Optional[int] = None,
) -> list[NavPlanType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Plan).order_by(Plan.id)
    if id is not None:
        statement = statement.where(Plan.id == id)
    if id_sys is not None:
        statement = statement.where(Plan.id_sys == id_sys)
    if cor_id is not None:
        statement = statement.where(Plan.cor_id == cor_id)
    if floor_id is not None:
        statement = statement.where(Plan.floor_id == floor_id)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_plan(record) for record in records]


async def create_nav_plan(info: Info, data: NavPlanInput) -> NavPlanType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    plan = Plan(
        id_sys=data.id_sys,
        cor_id=data.cor_id,
        floor_id=data.floor_id,
        ready=data.ready,
        entrances=DEFAULT_PLAN_ENTRANCES,
        graph=DEFAULT_PLAN_GRAPH,
        svg_id=None,
        nearest_entrance=data.nearest_entrance,
        nearest_man_wc=data.nearest_man_wc,
        nearest_woman_wc=data.nearest_woman_wc,
        nearest_shared_wc=data.nearest_shared_wc,
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return _to_nav_plan(plan)


async def update_nav_plan(info: Info, id: int, data: NavPlanUpdateInput) -> NavPlanType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    plan = await get_or_error(session, Plan, id, "plan")
    if data.id_sys is not None:
        plan.id_sys = data.id_sys
    if data.cor_id is not None:
        plan.cor_id = data.cor_id
    if data.floor_id is not None:
        plan.floor_id = data.floor_id
    if data.ready is not None:
        plan.ready = data.ready
    if data.nearest_entrance is not None:
        plan.nearest_entrance = data.nearest_entrance
    if data.nearest_man_wc is not None:
        plan.nearest_man_wc = data.nearest_man_wc
    if data.nearest_woman_wc is not None:
        plan.nearest_woman_wc = data.nearest_woman_wc
    if data.nearest_shared_wc is not None:
        plan.nearest_shared_wc = data.nearest_shared_wc
    await session.commit()
    await session.refresh(plan)
    return _to_nav_plan(plan)


async def delete_nav_plan(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    plan = await get_or_error(session, Plan, id, "plan")
    await session.delete(plan)
    await session.commit()
    return True
