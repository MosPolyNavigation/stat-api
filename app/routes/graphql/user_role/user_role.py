import strawberry
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional, List
from app.routes.graphql.pagination import PaginationInput, PageInfo, PaginationInfo
from app.routes.graphql.filter_handlers import _validated_limit_2, _validated_offset, _create_pagination_info
from app.routes.graphql.permissions import ensure_roles_view_permission
from app.models import UserRole
from .types import UserRoleType


@strawberry.type
class UserRoleConnection:
    """Connection тип для пагинации UserRole."""
    nodes: List[UserRoleType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class UserRoleFilterInput:
    """Фильтр для UserRole."""
    user_id: Optional[int] = None
    role_id: Optional[int] = None


def _to_user_role(model: UserRole) -> UserRoleType:
    """Конвертер модели SQLAlchemy в GraphQL тип."""
    # Импорты внутри функции для избежания циклического импорта
    from .user import _to_user_safe
    from .role import _to_role_safe
    
    return UserRoleType(
        user_id=model.user_id,
        role_id=model.role_id,
        user=_to_user_safe(model.user) if model.user else None,
        role=_to_role_safe(model.role) if model.role else None
    )


def _to_user_role_safe(model: UserRole) -> UserRoleType:
    """Конвертер модели SQLAlchemy в GraphQL тип."""
    from .role import _to_role_safe
    
    return UserRoleType(
        user_id=model.user_id,
        role_id=model.role_id,
        user=None,
        role=_to_role_safe(model.role) if model.role else None
    )


def _to_user_role_safe_2(model: UserRole) -> UserRoleType:
    """Конвертер модели SQLAlchemy в GraphQL тип."""
    from .user import _to_user_safe
    
    return UserRoleType(
        user_id=model.user_id,
        role_id=model.role_id,
        user=_to_user_safe(model.user) if model.user else None,
        role=None
    )


async def resolve_user_roles(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[UserRoleFilterInput] = None
) -> UserRoleConnection:
    """Резолвер для получения списка связей пользователь-роль."""
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    # Параметры пагинации
    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)
    
    # Базовый запрос с подгрузкой связанных данных
    statement = (
        select(UserRole)
        .options(
            selectinload(UserRole.user),
            selectinload(UserRole.role)
        )
        .order_by(UserRole.user_id, UserRole.role_id)
    )
    
    # Применение фильтров
    if filter:
        if filter.user_id is not None:
            statement = statement.where(UserRole.user_id == filter.user_id)
        if filter.role_id is not None:
            statement = statement.where(UserRole.role_id == filter.role_id)
    
    # Получение общего количества
    count_statement = select(func.count()).select_from(UserRole)
    if filter:
        if filter.user_id is not None:
            count_statement = count_statement.where(UserRole.user_id == filter.user_id)
        if filter.role_id is not None:
            count_statement = count_statement.where(UserRole.role_id == filter.role_id)
    
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
    
    return UserRoleConnection(
        nodes=[_to_user_role(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info
    )


async def resolve_user_role(
    info: Info,
    user_id: int,
    role_id: int
) -> Optional[UserRoleType]:
    """Резолвер для получения конкретной связи пользователь-роль."""
    session: AsyncSession = await ensure_roles_view_permission(info)
    
    statement = (
        select(UserRole)
        .options(
            selectinload(UserRole.user),
            selectinload(UserRole.role)
        )
        .where(UserRole.user_id == user_id)
        .where(UserRole.role_id == role_id)
    )
    
    result = (await session.execute(statement)).scalars().first()
    return _to_user_role(result) if result else None
