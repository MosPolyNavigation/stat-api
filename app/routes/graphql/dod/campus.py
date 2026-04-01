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
from app.models.dod.corpus import DodCorpus
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
from .types import DodNavCampusType


@strawberry.type
class DodNavCampusConnection:
    nodes: list[DodNavCampusType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class DodNavCampusInput:
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    comments: Optional[str] = None


@strawberry.input
class DodNavCampusUpdateInput:
    id_sys: Optional[str] = None
    loc_id: Optional[int] = None
    name: Optional[str] = None
    ready: Optional[bool] = None
    comments: Optional[str] = None


@strawberry.input
class DodNavCampusFilterInput:
    id: Optional[int] = None
    id_sys: Optional[str] = None
    loc_id: Optional[int] = None
    name: Optional[str] = None
    ready: Optional[bool] = None


def _to_dod_nav_campus(model: DodCorpus) -> DodNavCampusType:
    from .location import _to_dod_nav_location

    return DodNavCampusType(
        id=model.id,
        id_sys=model.id_sys,
        loc_id=model.loc_id,
        name=model.name,
        ready=model.ready,
        stair_groups=model.stair_groups,
        comments=model.comments,
        location=_to_dod_nav_location(model.locations) if model.locations else None,
    )


def _to_dod_nav_campus_safe(model: DodCorpus) -> DodNavCampusType:
    return DodNavCampusType(
        id=model.id,
        id_sys=model.id_sys,
        loc_id=model.loc_id,
        name=model.name,
        ready=model.ready,
        stair_groups=model.stair_groups,
        comments=model.comments,
        location=None,
    )


def _apply_campus_filters(statement, filter_data: Optional[DodNavCampusFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(DodCorpus.id == filter_data.id)
    if filter_data.id_sys is not None:
        statement = statement.where(DodCorpus.id_sys == filter_data.id_sys)
    if filter_data.loc_id is not None:
        statement = statement.where(DodCorpus.loc_id == filter_data.loc_id)
    if filter_data.name is not None:
        statement = statement.where(DodCorpus.name == filter_data.name)
    if filter_data.ready is not None:
        statement = statement.where(DodCorpus.ready == filter_data.ready)
    return statement


async def resolve_dod_nav_campuses(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[DodNavCampusFilterInput] = None,
) -> DodNavCampusConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_campus_filters(
        select(DodCorpus)
        .options(selectinload(DodCorpus.locations))
        .order_by(DodCorpus.id),
        filter,
    )
    count_statement = _apply_campus_filters(
        select(func.count()).select_from(DodCorpus),
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

    return DodNavCampusConnection(
        nodes=[_to_dod_nav_campus(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_dod_nav_campus(
    info: Info,
    data: DodNavCampusInput,
) -> DodNavCampusType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    campus = DodCorpus(
        id_sys=data.id_sys,
        loc_id=data.loc_id,
        name=data.name,
        ready=data.ready,
        stair_groups=None,
        comments=data.comments,
    )
    session.add(campus)
    await session.commit()
    await session.refresh(campus)
    return _to_dod_nav_campus_safe(campus)


async def update_dod_nav_campus(
    info: Info,
    id: int,
    data: DodNavCampusUpdateInput,
) -> DodNavCampusType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    campus = await get_or_error(session, DodCorpus, id, "campus")
    if data.id_sys is not None:
        campus.id_sys = data.id_sys
    if data.loc_id is not None:
        campus.loc_id = data.loc_id
    if data.name is not None:
        campus.name = data.name
    if data.ready is not None:
        campus.ready = data.ready
    if data.comments is not None:
        campus.comments = data.comments
    await session.commit()
    await session.refresh(campus)
    return _to_dod_nav_campus_safe(campus)


async def delete_dod_nav_campus(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    campus = await get_or_error(session, DodCorpus, id, "campus")
    await session.delete(campus)
    await session.commit()
    return True
