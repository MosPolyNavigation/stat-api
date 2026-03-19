import strawberry
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional, List
from app.routes.graphql.pagination import PaginationInput, PageInfo, PaginationInfo
from app.routes.graphql.filter_handlers import _validated_limit_2, _validated_offset, _create_pagination_info
from app.routes.graphql.permissions import ensure_roles_view_permission, ensure_roles_edit_permission
from app.models import Role, UserRole, RoleRightGoal
from .types import RoleType
from .inputs import RoleRightGoalInput, CreateRoleInput


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
    from .user_role import _to_user_role_safe
    
    return RoleType(
        id=model.id,
        name=model.name,
        role_right_goals=[_to_role_right_goal_safe(rrg) for rrg in model.role_right_goals] 
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
    """Мутация для создания новой роли с правами.
    
    ВАЖНО: Пользователь может назначить только те права, которые есть у него самого.
    """
    from graphql import GraphQLError
    from app.models import Right, Goal
    
    session: AsyncSession = await ensure_roles_edit_permission(info)
    
    current_user = info.context["current_user"]
    
    # Получаем права текущего пользователя
    user_rights = await current_user.get_rights(session)
    
    # Проверка на уникальность name
    existing_role = (
        await session.execute(
            select(Role).where(Role.name == data.name)
        )
    ).scalars().first()
    
    if existing_role:
        raise GraphQLError("Роль с таким названием уже существует")
    
    # Оптимизация: собираем все уникальные right_id и goal_id
    if data.role_right_goals:
        unique_right_ids = {rrg.right_id for rrg in data.role_right_goals}
        unique_goal_ids = {rrg.goal_id for rrg in data.role_right_goals}
        
        # Один запрос для всех прав
        rights_result = await session.execute(
            select(Right).where(Right.id.in_(unique_right_ids))
        )
        rights_map = {right.id: right for right in rights_result.scalars().all()}
        
        # Один запрос для всех целей
        goals_result = await session.execute(
            select(Goal).where(Goal.id.in_(unique_goal_ids))
        )
        goals_map = {goal.id: goal for goal in goals_result.scalars().all()}
        
        # Проверка: все ли права и цели найдены
        missing_rights = unique_right_ids - rights_map.keys()
        missing_goals = unique_goal_ids - goals_map.keys()
        
        if missing_rights:
            raise GraphQLError(f"Права с ID не найдены: {', '.join(map(str, missing_rights))}")
        if missing_goals:
            raise GraphQLError(f"Цели с ID не найдены: {', '.join(map(str, missing_goals))}")
        
        # Проверка прав пользователя и дубликатов
        missing_permissions = []
        seen_combinations = set()
        
        for rrg_input in data.role_right_goals:
            right = rights_map[rrg_input.right_id]
            goal = goals_map[rrg_input.goal_id]
            
            # Проверка дубликатов через set (O(1))
            combination_key = (rrg_input.right_id, rrg_input.goal_id)
            if combination_key in seen_combinations:
                raise GraphQLError(
                    f"Дублирующаяся связь: право {right.name} -> цель {goal.name}"
                )
            seen_combinations.add(combination_key)
            
            # Проверка: есть ли у пользователя это право для этой цели
            user_goal_rights = user_rights.get(goal.name, [])
            if right.name not in user_goal_rights:
                missing_permissions.append(f"{right.name} -> {goal.name}")
        
        # Если есть недостающие права — ошибка
        if missing_permissions:
            raise GraphQLError(
                f"Недостаточно прав для назначения следующих прав: {', '.join(missing_permissions)}. "
                f"Вы можете назначать только те права, которые есть у вас."
            )
    
    # Создание роли
    role = Role(name=data.name)
    session.add(role)
    await session.flush()  # Получаем ID роли до commit
    
    # Создание связей role_right_goals если указаны
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
    
    # Перезагружаем роль с связями для возврата полных данных
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
