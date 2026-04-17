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
from app.models.nav.types import Type as NavTypeModel
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
from .types import NavTypeType


@strawberry.type
class NavTypeConnection:
    nodes: list[NavTypeType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class NavTypeInput:
    name: str


@strawberry.input
class NavTypeUpdateInput:
    name: Optional[str] = None


@strawberry.input
class NavTypeFilterInput:
    id: Optional[int] = None
    name: Optional[str] = None


def _to_nav_type(model: NavTypeModel) -> NavTypeType:
    return NavTypeType(id=model.id, name=model.name)


def _apply_type_filters(statement, filter_data: Optional[NavTypeFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(NavTypeModel.id == filter_data.id)
    if filter_data.name is not None:
        statement = statement.where(NavTypeModel.name == filter_data.name)
    return statement


async def resolve_nav_types(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[NavTypeFilterInput] = None,
) -> NavTypeConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_type_filters(
        select(NavTypeModel).order_by(NavTypeModel.id),
        filter,
    )
    count_statement = _apply_type_filters(
        select(func.count()).select_from(NavTypeModel),
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

    return NavTypeConnection(
        nodes=[_to_nav_type(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_nav_type(info: Info, data: NavTypeInput) -> NavTypeType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    nav_type = NavTypeModel(name=data.name)
    session.add(nav_type)
    await session.commit()
    await session.refresh(nav_type)
    return _to_nav_type(nav_type)


async def update_nav_type(info: Info, id: int, data: NavTypeUpdateInput) -> NavTypeType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    nav_type = await get_or_error(session, NavTypeModel, id, "type")
    if data.name is not None:
        nav_type.name = data.name
    await session.commit()
    await session.refresh(nav_type)
    return _to_nav_type(nav_type)


async def delete_nav_type(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    nav_type = await get_or_error(session, NavTypeModel, id, "type")
    await session.delete(nav_type)
    await session.commit()
    return True
