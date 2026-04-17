from typing import Optional

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info

from app.constants import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
)
from app.models.nav.location import Location
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

from .common import get_or_error, validate_json_array
from .types import NavLocationType


@strawberry.type
class NavLocationConnection:
    nodes: list[NavLocationType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class NavLocationInput:
    id_sys: str
    name: str
    short: str
    ready: bool
    address: str
    metro: str
    comments: Optional[str] = None
    crossings: Optional[str] = None


@strawberry.input
class NavLocationUpdateInput:
    id_sys: Optional[str] = None
    name: Optional[str] = None
    short: Optional[str] = None
    ready: Optional[bool] = None
    address: Optional[str] = None
    metro: Optional[str] = None
    comments: Optional[str] = None
    crossings: Optional[str] = None


@strawberry.input
class NavLocationFilterInput:
    id: Optional[int] = None
    id_sys: Optional[str] = None
    name: Optional[str] = None
    short: Optional[str] = None
    ready: Optional[bool] = None


def _to_nav_location(model: Location) -> NavLocationType:
    return NavLocationType(
        id=model.id,
        id_sys=model.id_sys,
        name=model.name,
        short=model.short,
        ready=model.ready,
        address=model.address,
        metro=model.metro,
        crossings=model.crossings,
        comments=model.comments,
    )


def _apply_location_filters(statement, filter_data: Optional[NavLocationFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(Location.id == filter_data.id)
    if filter_data.id_sys is not None:
        statement = statement.where(Location.id_sys == filter_data.id_sys)
    if filter_data.name is not None:
        statement = statement.where(Location.name == filter_data.name)
    if filter_data.short is not None:
        statement = statement.where(Location.short == filter_data.short)
    if filter_data.ready is not None:
        statement = statement.where(Location.ready == filter_data.ready)
    return statement


async def resolve_nav_locations(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[NavLocationFilterInput] = None,
) -> NavLocationConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_location_filters(
        select(Location).order_by(Location.id),
        filter,
    )
    count_statement = _apply_location_filters(
        select(func.count()).select_from(Location),
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

    return NavLocationConnection(
        nodes=[_to_nav_location(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_nav_location(info: Info, data: NavLocationInput) -> NavLocationType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    location = Location(
        id_sys=data.id_sys,
        name=data.name,
        short=data.short,
        ready=data.ready,
        address=data.address,
        metro=data.metro,
        crossings=validate_json_array(data.crossings, "crossings"),
        comments=data.comments,
    )
    session.add(location)
    await session.commit()
    await session.refresh(location)
    return _to_nav_location(location)


async def update_nav_location(info: Info, id: int, data: NavLocationUpdateInput) -> NavLocationType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    location = await get_or_error(session, Location, id, "location")
    if data.id_sys is not None:
        location.id_sys = data.id_sys
    if data.name is not None:
        location.name = data.name
    if data.short is not None:
        location.short = data.short
    if data.ready is not None:
        location.ready = data.ready
    if data.address is not None:
        location.address = data.address
    if data.metro is not None:
        location.metro = data.metro
    if data.comments is not None:
        location.comments = data.comments
    if data.crossings is not None:
        location.crossings = validate_json_array(data.crossings, "crossings")
    await session.commit()
    await session.refresh(location)
    return _to_nav_location(location)


async def delete_nav_location(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    location = await get_or_error(session, Location, id, "location")
    await session.delete(location)
    await session.commit()
    return True
