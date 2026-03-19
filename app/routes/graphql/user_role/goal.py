import strawberry
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info
from typing import Optional, List
from app.routes.graphql.pagination import PaginationInput, PageInfo, PaginationInfo
from app.routes.graphql.filter_handlers import _validated_limit_2, _validated_offset, _create_pagination_info
from app.routes.graphql.permissions import ensure_roles_view_permission
from app.models import Goal
from .types import GoalType


@strawberry.type
class GoalConnection:
    nodes: List[GoalType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class GoalFilterInput:
    id: Optional[int] = None
    name: Optional[str] = None


def _to_goal(model: Goal) -> GoalType:
    return GoalType(id=model.id, name=model.name)


async def resolve_goals(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[GoalFilterInput] = None
) -> GoalConnection:
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)
    
    statement = select(Goal).order_by(Goal.id)
    
    if filter:
        if filter.id is not None:
            statement = statement.where(Goal.id == filter.id)
        if filter.name is not None:
            statement = statement.where(Goal.name == filter.name)
    
    count_statement = select(func.count()).select_from(Goal)
    if filter:
        if filter.id is not None:
            count_statement = count_statement.where(Goal.id == filter.id)
        if filter.name is not None:
            count_statement = count_statement.where(Goal.name == filter.name)
    
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
    
    return GoalConnection(
        nodes=[_to_goal(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info
    )
