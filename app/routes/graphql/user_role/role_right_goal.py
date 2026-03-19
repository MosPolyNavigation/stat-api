import strawberry
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional, List
from app.routes.graphql.pagination import PaginationInput, PageInfo, PaginationInfo
from app.routes.graphql.filter_handlers import _validated_limit_2, _validated_offset, _create_pagination_info
from app.routes.graphql.permissions import ensure_roles_view_permission
from app.models.auth.role_right_goal import RoleRightGoal
from .types import RoleRightGoalType


@strawberry.type
class RoleRightGoalConnection:
    """Connection тип для пагинации RoleRightGoal."""
    nodes: List[RoleRightGoalType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class RoleRightGoalFilterInput:
    """Фильтр для RoleRightGoal."""
    role_id: Optional[int] = None
    right_id: Optional[int] = None
    goal_id: Optional[int] = None


def _to_role_right_goal(model: RoleRightGoal) -> RoleRightGoalType:
    """Конвертер модели SQLAlchemy в GraphQL тип."""
    # Импорты внутри функции для избежания циклического импорта
    from .role import _to_role_safe
    from .right import _to_right
    from .goal import _to_goal
    
    return RoleRightGoalType(
        role_id=model.role_id,
        right_id=model.right_id,
        goal_id=model.goal_id,
        role=_to_role_safe(model.role) if model.role else None,
        right=_to_right(model.right) if model.right else None,
        goal=_to_goal(model.goal) if model.goal else None
    )


async def resolve_role_right_goals(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[RoleRightGoalFilterInput] = None
) -> RoleRightGoalConnection:
    """Резолвер для получения списка связей роль-право-цель."""
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    # Параметры пагинации
    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)
    
    # Базовый запрос с подгрузкой связанных данных
    statement = (
        select(RoleRightGoal)
        .options(
            selectinload(RoleRightGoal.role),
            selectinload(RoleRightGoal.right),
            selectinload(RoleRightGoal.goal)
        )
        .order_by(RoleRightGoal.role_id, RoleRightGoal.right_id, RoleRightGoal.goal_id)
    )
    
    # Применение фильтров
    if filter:
        if filter.role_id is not None:
            statement = statement.where(RoleRightGoal.role_id == filter.role_id)
        if filter.right_id is not None:
            statement = statement.where(RoleRightGoal.right_id == filter.right_id)
        if filter.goal_id is not None:
            statement = statement.where(RoleRightGoal.goal_id == filter.goal_id)
    
    # Получение общего количества
    count_statement = select(func.count()).select_from(RoleRightGoal)
    if filter:
        if filter.role_id is not None:
            count_statement = count_statement.where(RoleRightGoal.role_id == filter.role_id)
        if filter.right_id is not None:
            count_statement = count_statement.where(RoleRightGoal.right_id == filter.right_id)
        if filter.goal_id is not None:
            count_statement = count_statement.where(RoleRightGoal.goal_id == filter.goal_id)
    
    total_count_result = await session.execute(count_statement)
    total_count = total_count_result.scalar() or 0
    
    # Применение пагинации
    if offset > 0:
        statement = statement.offset(offset)
    if limit > 0:
        statement = statement.limit(limit)
    
    records = (await session.execute(statement)).scalars().all()
    records_count = len(records)
    
    # Создание информации о пагинации
    page_info, pagination_info = _create_pagination_info(
        total_count=total_count,
        offset=offset,
        limit=limit,
        records_count=records_count
    )
    
    return RoleRightGoalConnection(
        nodes=[_to_role_right_goal(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info
    )


async def resolve_role_right_goal(
    info: Info,
    role_id: int,
    right_id: int,
    goal_id: int
) -> Optional[RoleRightGoalType]:
    """Резолвер для получения конкретной связи роль-право-цель."""
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    statement = (
        select(RoleRightGoal)
        .options(
            selectinload(RoleRightGoal.role),
            selectinload(RoleRightGoal.right),
            selectinload(RoleRightGoal.goal)
        )
        .where(RoleRightGoal.role_id == role_id)
        .where(RoleRightGoal.right_id == right_id)
        .where(RoleRightGoal.goal_id == goal_id)
    )
    
    result = (await session.execute(statement)).scalars().first()
    return _to_role_right_goal(result) if result else None
