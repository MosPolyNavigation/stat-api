import strawberry
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional, List
from pwdlib import PasswordHash
from app.routes.graphql.pagination import PaginationInput, PageInfo, PaginationInfo
from app.routes.graphql.filter_handlers import _validated_limit_2, _validated_offset, _create_pagination_info
from app.routes.graphql.permissions import ensure_users_view_permission, ensure_users_create_permission
from app.models import User, UserRole
from .types import UserType
from .inputs import CreateUserInput


password_hash = PasswordHash.recommended()


@strawberry.type
class UserConnection:
    nodes: List[UserType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class UserFilterInput:
    id: Optional[int] = None
    login: Optional[str] = None
    is_active: Optional[bool] = None


def _to_user(model: User) -> UserType:
    from .user_role import _to_user_role_safe
    
    return UserType(
        id=model.id,
        login=model.login,
        fio=model.fio,
        is_active=model.is_active,
        registration_date=model.registration_date,
        updated_at=model.updated_at,
        roles=[_to_user_role_safe(ur) for ur in model.user_roles] if model.user_roles else None
    )

def _to_user_safe(model: User) -> UserType:
    return UserType(
        id=model.id,
        login=model.login,
        fio=model.fio,
        is_active=model.is_active,
        registration_date=model.registration_date,
        updated_at=model.updated_at,
        roles=None
    )


async def resolve_users(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[UserFilterInput] = None
) -> UserConnection:
    session: AsyncSession = await ensure_users_view_permission(info)
    
    # Параметры пагинации
    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)
    
    # Базовый запрос
    statement = (
        select(User)
        .options(
            selectinload(User.user_roles)
            .selectinload(UserRole.role)
        )
        .order_by(User.id)
    )
    
    # Применение фильтров
    if filter:
        if filter.id is not None:
            statement = statement.where(User.id == filter.id)
        if filter.login is not None:
            statement = statement.where(User.login == filter.login)
        if filter.is_active is not None:
            statement = statement.where(User.is_active == filter.is_active)
    
    # Получение общего количества
    count_statement = select(func.count()).select_from(User)
    if filter:
        if filter.id is not None:
            count_statement = count_statement.where(User.id == filter.id)
        if filter.login is not None:
            count_statement = count_statement.where(User.login == filter.login)
        if filter.is_active is not None:
            count_statement = count_statement.where(User.is_active == filter.is_active)
    
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
    
    return UserConnection(
        nodes=[_to_user(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info
    )


async def resolve_user(info: Info, user_id: int) -> Optional[UserType]:
    session: AsyncSession = await ensure_users_view_permission(info)
    
    statement = (
        select(User)
        .options(
            selectinload(User.user_roles)
            .selectinload(UserRole.role)
        )
        .where(User.id == user_id)
    )
    
    result = (await session.execute(statement)).scalars().first()
    return _to_user(result) if result else None


async def create_user(info: Info, data: CreateUserInput) -> UserType:
    """Мутация для создания нового пользователя."""
    session: AsyncSession = await ensure_users_create_permission(info)
    
    # Проверка на уникальность login
    existing_user = (
        await session.execute(
            select(User).where(User.login == data.login)
        )
    ).scalars().first()
    
    if existing_user:
        from graphql import GraphQLError
        raise GraphQLError("Пользователь с таким логином уже существует")
    
    # Хэширование пароля
    hashed_password = password_hash.hash(data.password)
    
    # Создание пользователя
    user = User(
        login=data.login,
        hash=hashed_password,
        fio=data.fio,
        is_active=data.is_active
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return _to_user_safe(user)
