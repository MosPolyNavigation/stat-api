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
from app.models.nav.floor import Floor
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
from .types import NavFloorType


@strawberry.type
class NavFloorConnection:
    nodes: list[NavFloorType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class NavFloorInput:
    name: int


@strawberry.input
class NavFloorUpdateInput:
    name: Optional[int] = None


@strawberry.input
class NavFloorFilterInput:
    id: Optional[int] = None
    name: Optional[int] = None


def _to_nav_floor(model: Floor) -> NavFloorType:
    return NavFloorType(id=model.id, name=model.name)


def _apply_floor_filters(statement, filter_data: Optional[NavFloorFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(Floor.id == filter_data.id)
    if filter_data.name is not None:
        statement = statement.where(Floor.name == filter_data.name)
    return statement


async def resolve_nav_floors(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[NavFloorFilterInput] = None,
) -> NavFloorConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_floor_filters(
        select(Floor).order_by(Floor.id),
        filter,
    )
    count_statement = _apply_floor_filters(
        select(func.count()).select_from(Floor),
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

    return NavFloorConnection(
        nodes=[_to_nav_floor(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_nav_floor(info: Info, data: NavFloorInput) -> NavFloorType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    floor = Floor(name=data.name)
    session.add(floor)
    await session.commit()
    await session.refresh(floor)
    return _to_nav_floor(floor)


async def update_nav_floor(info: Info, id: int, data: NavFloorUpdateInput) -> NavFloorType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    floor = await get_or_error(session, Floor, id, "floor")
    if data.name is not None:
        floor.name = data.name
    await session.commit()
    await session.refresh(floor)
    return _to_nav_floor(floor)


async def delete_nav_floor(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    floor = await get_or_error(session, Floor, id, "floor")
    await session.delete(floor)
    await session.commit()
    return True
