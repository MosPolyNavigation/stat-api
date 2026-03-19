import strawberry
from graphql import GraphQLError
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional, List
from app.routes.graphql.pagination import (
    PaginationInput, PageInfo, PaginationInfo
)
from app.routes.graphql.filter_handlers import (
    _validated_limit_2, _validated_offset, _create_pagination_info
)
from app.routes.graphql.permissions import (
    ensure_roles_view_permission,
    ensure_roles_edit_permission,
    validate_user_permissions_by_ids,
    validate_role_right_goals_duplicates
)
from app.models import Role, UserRole, RoleRightGoal
from .types import RoleType
from .inputs import RoleRightGoalInput, CreateRoleInput, UpdateRoleInput


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
    from .role_right_goal import _to_role_right_goal_safe
    from .user_role import _to_user_role_safe_2
    
    return RoleType(
        id=model.id,
        name=model.name,
        role_right_goals=[_to_role_right_goal_safe(rrg) for rrg in model.role_right_goals] 
        if model.role_right_goals else None,
        user_roles=[_to_user_role_safe_2(ur) for ur in model.user_roles] 
        if model.user_roles else None
    )


def _to_role_safe(model: Role) -> RoleType:
    return RoleType(
        id=model.id,
        name=model.name,
        role_right_goals=None,
        user_roles=None
    )


def _to_role_safe_2(model: Role) -> RoleType:
    from .role_right_goal import _to_role_right_goal_safe
    from .user_role import _to_user_role_safe
    
    return RoleType(
        id=model.id,
        name=model.name,
        role_right_goals=[_to_role_right_goal_safe(rrg) for rrg in model.role_right_goals] 
        if model.role_right_goals else None,
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


async def create_role(info: Info, data: CreateRoleInput) -> RoleType:
    """Мутация для создания новой роли с правами."""
    session: AsyncSession = await ensure_roles_create_permission(info)
    current_user = info.context["current_user"]
    
    # 1. Проверка на уникальность name
    existing_role = (
        await session.execute(
            select(Role).where(Role.name == data.name)
        )
    ).scalars().first()
    
    if existing_role:
        raise GraphQLError("Роль с таким названием уже существует")
    
    # 2. Валидация прав и существования ID через единую функцию
    if data.role_right_goals:
        required_permissions = [
            (rrg.right_id, rrg.goal_id)
            for rrg in data.role_right_goals
        ]
        
        missing = await validate_user_permissions_by_ids(
            current_user, 
            session, 
            required_permissions
        )
        
        if missing:
            raise GraphQLError(
                f"Недостаточно прав для назначения следующих прав: {', '.join(missing)}. "
                f"Вы можете назначать только те права, которые есть у вас."
            )
        
        # 3. Проверка на дубликаты в рамках запроса
        await validate_role_right_goals_duplicates(session, data.role_right_goals)
    
    # 4. Создание роли
    role = Role(name=data.name)
    session.add(role)
    await session.flush()
    
    # 5. Создание связей role_right_goals
    if data.role_right_goals:
        for rrg_input in data.role_right_goals:
            rrg = RoleRightGoal(
                role_id=role.id,
                right_id=rrg_input.right_id,
                goal_id=rrg_input.goal_id
            )
            session.add(rrg)
    
    await session.commit()
    await session.refresh(role)
    
    # 6. Перезагружаем роль с связями для возврата полных данных
    statement = (
        select(Role)
        .options(
            selectinload(Role.role_right_goals)
            .selectinload(RoleRightGoal.right),
            selectinload(Role.role_right_goals)
            .selectinload(RoleRightGoal.goal)
        )
        .where(Role.id == role.id)
    )
    
    role_with_relations = (await session.execute(statement)).scalars().first()
    return _to_role_safe_2(role_with_relations)


async def update_role(info: Info, role_id: int, data: UpdateRoleInput) -> RoleType:
    """Мутация для редактирования роли.
    
    ВАЖНО: 
    1. Пользователь должен иметь право roles -> edit
    2. Нельзя добавить права, которых нет у текущего пользователя (защита от эскалации)
    3. При обновлении прав старые права удаляются и создаются новые
    """
    session: AsyncSession = await ensure_roles_edit_permission(info)
    current_user = info.context["current_user"]
    
    # Проверяем существование роли
    role = (
        await session.execute(
            select(Role).where(Role.id == role_id)
        )
    ).scalars().first()
    
    if not role:
        raise GraphQLError(f"Роль с ID {role_id} не найдена")
    
    # Обновляем name если предоставлен
    if data.name is not None:
        # Проверка на уникальность name (исключая текущую роль)
        existing_role = (
            await session.execute(
                select(Role).where(Role.name == data.name).where(Role.id != role_id)
            )
        ).scalars().first()
        
        if existing_role:
            raise GraphQLError("Роль с таким названием уже существует")
        
        role.name = data.name
    
    # Обновляем права роли если предоставлены
    if data.role_right_goals is not None:
        # Собираем список требуемых прав для проверки
        required_permissions = [
            (rrg.right_id, rrg.goal_id)
            for rrg in data.role_right_goals
        ]
        
        # Проверяем права пользователя через универсальную функцию
        missing = await validate_user_permissions_by_ids(
            current_user, 
            session, 
            required_permissions
        )
        
        if missing:
            raise GraphQLError(
                f"Недостаточно прав для назначения следующих прав: {', '.join(missing)}. "
                f"Вы можете назначать только те права, которые есть у вас."
            )
        
        # Проверка на дубликаты в рамках запроса
        await validate_role_right_goals_duplicates(session, data.role_right_goals)
        
        # Удаляем старые права роли
        old_rights = (
            await session.execute(
                select(RoleRightGoal).where(RoleRightGoal.role_id == role_id)
            )
        ).scalars().all()
        
        for old_right in old_rights:
            await session.delete(old_right)
        
        await session.flush()
        
        # Создаем новые права
        for rrg_input in data.role_right_goals:
            rrg = RoleRightGoal(
                role_id=role.id,
                right_id=rrg_input.right_id,
                goal_id=rrg_input.goal_id
            )
            session.add(rrg)
    
    await session.commit()
    await session.refresh(role)
    
    # Перезагружаем роль с связями для возврата полных данных
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
    
    role_with_relations = (await session.execute(statement)).scalars().first()
    return _to_role(role_with_relations)
