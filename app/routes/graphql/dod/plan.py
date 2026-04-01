from typing import Optional

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info

from app.constants import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
)
from app.models.dod.plan import DodPlan
from app.routes.graphql.filter_handlers import (
    _create_pagination_info,
    _validated_limit_2,
    _validated_offset,
)
from app.routes.graphql.pagination import (
    PageInfo,
    PaginationInfo,
    PaginationInput,
)
from app.routes.graphql.permissions import ensure_nav_permission

from .common import get_or_error
from .types import DodNavPlanType


DEFAULT_PLAN_ENTRANCES = "[]"
DEFAULT_PLAN_GRAPH = "{}"


@strawberry.type
class DodNavPlanConnection:
    nodes: list[DodNavPlanType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class DodNavPlanInput:
    id_sys: str
    cor_id: int
    floor_id: int
    ready: bool
    nearest_entrance: Optional[str] = None
    nearest_man_wc: Optional[str] = None
    nearest_woman_wc: Optional[str] = None
    nearest_shared_wc: Optional[str] = None


@strawberry.input
class DodNavPlanUpdateInput:
    id_sys: Optional[str] = None
    cor_id: Optional[int] = None
    floor_id: Optional[int] = None
    ready: Optional[bool] = None
    nearest_entrance: Optional[str] = None
    nearest_man_wc: Optional[str] = None
    nearest_woman_wc: Optional[str] = None
    nearest_shared_wc: Optional[str] = None


@strawberry.input
class DodNavPlanFilterInput:
    id: Optional[int] = None
    id_sys: Optional[str] = None
    cor_id: Optional[int] = None
    floor_id: Optional[int] = None
    ready: Optional[bool] = None
    svg_id: Optional[int] = None


def _to_dod_nav_plan(model: DodPlan) -> DodNavPlanType:
    from .campus import _to_dod_nav_campus_safe
    from .floor import _to_dod_nav_floor
    from .static import _to_dod_nav_static

    return DodNavPlanType(
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
        campus=_to_dod_nav_campus_safe(model.corpus) if model.corpus else None,
        floor=_to_dod_nav_floor(model.floor) if model.floor else None,
        svg=_to_dod_nav_static(model.svg) if model.svg else None,
    )


def _to_dod_nav_plan_safe(model: DodPlan) -> DodNavPlanType:
    return DodNavPlanType(
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
        campus=None,
        floor=None,
        svg=None,
    )


def _apply_plan_filters(statement, filter_data: Optional[DodNavPlanFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(DodPlan.id == filter_data.id)
    if filter_data.id_sys is not None:
        statement = statement.where(DodPlan.id_sys == filter_data.id_sys)
    if filter_data.cor_id is not None:
        statement = statement.where(DodPlan.cor_id == filter_data.cor_id)
    if filter_data.floor_id is not None:
        statement = statement.where(DodPlan.floor_id == filter_data.floor_id)
    if filter_data.ready is not None:
        statement = statement.where(DodPlan.ready == filter_data.ready)
    if filter_data.svg_id is not None:
        statement = statement.where(DodPlan.svg_id == filter_data.svg_id)
    return statement


async def resolve_dod_nav_plans(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[DodNavPlanFilterInput] = None,
) -> DodNavPlanConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_plan_filters(
        select(DodPlan)
        .options(
            selectinload(DodPlan.corpus),
            selectinload(DodPlan.floor),
            selectinload(DodPlan.svg),
        )
        .order_by(DodPlan.id),
        filter,
    )
    count_statement = _apply_plan_filters(
        select(func.count()).select_from(DodPlan),
        filter,
    )

    total_count = (await session.execute(count_statement)).scalar() or 0

    if offset > 0:
        statement = statement.offset(offset)
    if limit > 0:
        statement = statement.limit(limit)

    records = (await session.execute(statement)).scalars().all()
    page_info, pagination_info = _create_pagination_info(
        total_count=total_count,
        offset=offset,
        limit=limit,
        records_count=len(records),
    )

    return DodNavPlanConnection(
        nodes=[_to_dod_nav_plan(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_dod_nav_plan(info: Info, data: DodNavPlanInput) -> DodNavPlanType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    plan = DodPlan(
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
    return _to_dod_nav_plan_safe(plan)


async def update_dod_nav_plan(
    info: Info,
    id: int,
    data: DodNavPlanUpdateInput,
) -> DodNavPlanType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    plan = await get_or_error(session, DodPlan, id, "plan")
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
    return _to_dod_nav_plan_safe(plan)


async def delete_dod_nav_plan(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    plan = await get_or_error(session, DodPlan, id, "plan")
    await session.delete(plan)
    await session.commit()
    return True
