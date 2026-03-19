import strawberry
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info
from typing import Optional, List
from app.routes.graphql.pagination import PaginationInput, PageInfo, PaginationInfo
from app.routes.graphql.filter_handlers import _validated_limit_2, _validated_offset, _create_pagination_info
from app.routes.graphql.permissions import ensure_roles_view_permission
from app.models import Right
from .types import RightType


@strawberry.type
class RightConnection:
    nodes: List[RightType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class RightFilterInput:
    id: Optional[int] = None
    name: Optional[str] = None


def _to_right(model: Right) -> RightType:
    return RightType(id=model.id, name=model.name)


async def resolve_rights(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[RightFilterInput] = None
) -> RightConnection:
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)
    
    statement = select(Right).order_by(Right.id)
    
    if filter:
        if filter.id is not None:
            statement = statement.where(Right.id == filter.id)
        if filter.name is not None:
            statement = statement.where(Right.name == filter.name)
    
    count_statement = select(func.count()).select_from(Right)
    if filter:
        if filter.id is not None:
            count_statement = count_statement.where(Right.id == filter.id)
        if filter.name is not None:
            count_statement = count_statement.where(Right.name == filter.name)
    
    total_count_result = await session.execute(count_statement)
    total_count = total_count_result.scalar() or 0
    
    if offset > 0:
        statement = statement.offset(offset)
    if limit > 0:
        statement = statement.limit(limit)
    
    records = (await session.execute(statement)).scalars().all()
    records_count = len(records)
    
    page_info, pagination_info = _create_pagination_info(
        total_count=total_count,
        offset=offset,
        limit=limit,
        records_count=records_count
    )
    
    return RightConnection(
        nodes=[_to_right(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info
    )
