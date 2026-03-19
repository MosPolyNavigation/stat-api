import strawberry
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional, List
from app.routes.graphql.pagination import PaginationInput, PageInfo, PaginationInfo
from app.routes.graphql.filter_handlers import _validated_limit_2, _validated_offset, _create_pagination_info
from app.routes.graphql.permissions import ensure_roles_view_permission
from app.models import Role, UserRole, RoleRightGoal
from .types import RoleType


@strawberry.type
class RoleConnection:
    nodes: List[RoleType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class RoleFilterInput:
    id: Optional[int] = None
    name: Optional[str] = None


def _to_role(model: Role) -> RoleType:
    from .role_right_goal import _to_role_right_goal
    from .user_role import _to_user_role_safe
    
    return RoleType(
        id=model.id,
        name=model.name,
        role_right_goals=[_to_role_right_goal(rrg) for rrg in model.role_right_goals] 
        if model.role_right_goals else None,
        user_roles=[_to_user_role_safe(ur) for ur in model.user_roles] 
        if model.user_roles else None
    )


def _to_role_safe(model: Role) -> RoleType:
    return RoleType(
        id=model.id,
        name=model.name,
        role_right_goals=None,
        user_roles=None
    )


async def resolve_roles(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[RoleFilterInput] = None
) -> RoleConnection:
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)
    
    statement = (
        select(Role)
        .options(
            selectinload(Role.role_right_goals)
            .selectinload(RoleRightGoal.right),
            selectinload(Role.role_right_goals)
            .selectinload(RoleRightGoal.goal),
            selectinload(Role.user_roles)
            .selectinload(UserRole.user)
        )
        .order_by(Role.id)
    )
    
    if filter:
        if filter.id is not None:
            statement = statement.where(Role.id == filter.id)
        if filter.name is not None:
            statement = statement.where(Role.name == filter.name)
    
    count_statement = select(func.count()).select_from(Role)
    if filter:
        if filter.id is not None:
            count_statement = count_statement.where(Role.id == filter.id)
        if filter.name is not None:
            count_statement = count_statement.where(Role.name == filter.name)
    
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
    
    return RoleConnection(
        nodes=[_to_role(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info
    )


async def resolve_role(info: Info, role_id: int) -> Optional[RoleType]:
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    statement = (
        select(Role)
        .options(
            selectinload(Role.role_right_goals)
            .selectinload(RoleRightGoal.right),
            selectinload(Role.role_right_goals)
            .selectinload(RoleRightGoal.goal),
            selectinload(Role.user_roles)
            .selectinload(UserRole.user)
        )
        .where(Role.id == role_id)
    )
    
    result = (await session.execute(statement)).scalars().first()
    return _to_role(result) if result else None
