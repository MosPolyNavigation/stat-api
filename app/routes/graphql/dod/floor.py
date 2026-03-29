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
from app.models.dod.floor import DodFloor
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
from .types import DodNavFloorType


@strawberry.type
class DodNavFloorConnection:
    nodes: list[DodNavFloorType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class DodNavFloorInput:
    name: int


@strawberry.input
class DodNavFloorUpdateInput:
    name: Optional[int] = None


@strawberry.input
class DodNavFloorFilterInput:
    id: Optional[int] = None
    name: Optional[int] = None


def _to_dod_nav_floor(model: DodFloor) -> DodNavFloorType:
    return DodNavFloorType(id=model.id, name=model.name)


def _apply_floor_filters(statement, filter_data: Optional[DodNavFloorFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(DodFloor.id == filter_data.id)
    if filter_data.name is not None:
        statement = statement.where(DodFloor.name == filter_data.name)
    return statement


async def resolve_dod_nav_floors(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[DodNavFloorFilterInput] = None,
) -> DodNavFloorConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_floor_filters(
        select(DodFloor).order_by(DodFloor.id),
        filter,
    )
    count_statement = _apply_floor_filters(
        select(func.count()).select_from(DodFloor),
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

    return DodNavFloorConnection(
        nodes=[_to_dod_nav_floor(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_dod_nav_floor(info: Info, data: DodNavFloorInput) -> DodNavFloorType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    floor = DodFloor(name=data.name)
    session.add(floor)
    await session.commit()
    await session.refresh(floor)
    return _to_dod_nav_floor(floor)


async def update_dod_nav_floor(
    info: Info,
    id: int,
    data: DodNavFloorUpdateInput,
) -> DodNavFloorType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    floor = await get_or_error(session, DodFloor, id, "floor")
    if data.name is not None:
        floor.name = data.name
    await session.commit()
    await session.refresh(floor)
    return _to_dod_nav_floor(floor)


async def delete_dod_nav_floor(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    floor = await get_or_error(session, DodFloor, id, "floor")
    await session.delete(floor)
    await session.commit()
    return True
