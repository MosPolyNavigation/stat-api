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
from app.models.nav.static import Static
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
from .types import NavStaticType


@strawberry.type
class NavStaticConnection:
    nodes: list[NavStaticType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class NavStaticInput:
    ext: str
    path: str
    name: str
    link: str


@strawberry.input
class NavStaticUpdateInput:
    ext: Optional[str] = None
    path: Optional[str] = None
    name: Optional[str] = None
    link: Optional[str] = None


@strawberry.input
class NavStaticFilterInput:
    id: Optional[int] = None
    name: Optional[str] = None
    ext: Optional[str] = None
    link: Optional[str] = None


def _to_nav_static(model: Static) -> NavStaticType:
    return NavStaticType(
        id=model.id,
        ext=model.ext,
        path=model.path,
        name=model.name,
        link=model.link,
        creation_date=model.creation_date,
        update_date=model.update_date,
    )


def _apply_static_filters(statement, filter_data: Optional[NavStaticFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(Static.id == filter_data.id)
    if filter_data.name is not None:
        statement = statement.where(Static.name == filter_data.name)
    if filter_data.ext is not None:
        statement = statement.where(Static.ext == filter_data.ext)
    if filter_data.link is not None:
        statement = statement.where(Static.link == filter_data.link)
    return statement


async def resolve_nav_statics(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[NavStaticFilterInput] = None,
) -> NavStaticConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_static_filters(
        select(Static).order_by(Static.id),
        filter,
    )
    count_statement = _apply_static_filters(
        select(func.count()).select_from(Static),
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

    return NavStaticConnection(
        nodes=[_to_nav_static(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_nav_static(info: Info, data: NavStaticInput) -> NavStaticType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    static = Static(
        ext=data.ext,
        path=data.path,
        name=data.name,
        link=data.link,
    )
    session.add(static)
    await session.commit()
    await session.refresh(static)
    return _to_nav_static(static)


async def update_nav_static(info: Info, id: int, data: NavStaticUpdateInput) -> NavStaticType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    static = await get_or_error(session, Static, id, "static file")
    if data.ext is not None:
        static.ext = data.ext
    if data.path is not None:
        static.path = data.path
    if data.name is not None:
        static.name = data.name
    if data.link is not None:
        static.link = data.link
    await session.commit()
    await session.refresh(static)
    return _to_nav_static(static)


async def delete_nav_static(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    static = await get_or_error(session, Static, id, "static file")
    await session.delete(static)
    await session.commit()
    return True
