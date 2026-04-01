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
from app.models.nav.corpus import Corpus
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
from .types import NavCampusType


@strawberry.type
class NavCampusConnection:
    nodes: list[NavCampusType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class NavCampusInput:
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    comments: Optional[str] = None


@strawberry.input
class NavCampusUpdateInput:
    id_sys: Optional[str] = None
    loc_id: Optional[int] = None
    name: Optional[str] = None
    ready: Optional[bool] = None
    comments: Optional[str] = None


@strawberry.input
class NavCampusFilterInput:
    id: Optional[int] = None
    id_sys: Optional[str] = None
    loc_id: Optional[int] = None
    name: Optional[str] = None
    ready: Optional[bool] = None


def _to_nav_campus(model: Corpus) -> NavCampusType:
    from .location import _to_nav_location

    return NavCampusType(
        id=model.id,
        id_sys=model.id_sys,
        loc_id=model.loc_id,
        name=model.name,
        ready=model.ready,
        stair_groups=model.stair_groups,
        comments=model.comments,
        location=_to_nav_location(model.locations) if model.locations else None,
    )


def _to_nav_campus_safe(model: Corpus) -> NavCampusType:
    return NavCampusType(
        id=model.id,
        id_sys=model.id_sys,
        loc_id=model.loc_id,
        name=model.name,
        ready=model.ready,
        stair_groups=model.stair_groups,
        comments=model.comments,
        location=None,
    )


def _apply_campus_filters(statement, filter_data: Optional[NavCampusFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(Corpus.id == filter_data.id)
    if filter_data.id_sys is not None:
        statement = statement.where(Corpus.id_sys == filter_data.id_sys)
    if filter_data.loc_id is not None:
        statement = statement.where(Corpus.loc_id == filter_data.loc_id)
    if filter_data.name is not None:
        statement = statement.where(Corpus.name == filter_data.name)
    if filter_data.ready is not None:
        statement = statement.where(Corpus.ready == filter_data.ready)
    return statement


async def resolve_nav_campuses(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[NavCampusFilterInput] = None,
) -> NavCampusConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_campus_filters(
        select(Corpus)
        .options(selectinload(Corpus.locations))
        .order_by(Corpus.id),
        filter,
    )
    count_statement = _apply_campus_filters(
        select(func.count()).select_from(Corpus),
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

    return NavCampusConnection(
        nodes=[_to_nav_campus(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_nav_campus(info: Info, data: NavCampusInput) -> NavCampusType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    campus = Corpus(
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
    return _to_nav_campus_safe(campus)


async def update_nav_campus(info: Info, id: int, data: NavCampusUpdateInput) -> NavCampusType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    campus = await get_or_error(session, Corpus, id, "campus")
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
    return _to_nav_campus_safe(campus)


async def delete_nav_campus(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    campus = await get_or_error(session, Corpus, id, "campus")
    await session.delete(campus)
    await session.commit()
    return True
