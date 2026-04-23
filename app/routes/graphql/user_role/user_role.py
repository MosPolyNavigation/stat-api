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
)
from app.services.permission_service import PermissionService
from app.models import UserRole, User, Role, RoleRightGoal
from .types import UserRoleType, GrantRoleResult, UserType
from .inputs import GrantRoleInput


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


async def grant_role(info: Info, data: GrantRoleInput) -> GrantRoleResult:
    """Мутация для назначения роли(ей) пользователю.
    
    ВАЖНО: 
    Нельзя назначить роль, если у пользователя нет соответствующих прав с can_grant = True, которые содержатся в этой роли.
    (защита от эскалации привилегий)
    """
    session: AsyncSession = info.context["db"]
    current_user = info.context["current_user"]
    service: PermissionService = info.context["permission_service"]
    
    # Проверяем существование пользователя
    target_user = (
        await session.execute(
            select(User).where(User.id == data.user_id)
        )
    ).scalars().first()
    
    if not target_user:
        raise GraphQLError(f"Пользователь с ID {data.user_id} не найден")
    
    if not target_user.is_active:
        raise GraphQLError("Нельзя назначить роль неактивному пользователю")
    
    # Получаем все роли одним запросом
    roles_result = await session.execute(
        select(Role).where(Role.id.in_(data.role_ids))
    )
    roles_map = {role.id: role for role in roles_result.scalars().all()}
    
    # Проверяем, все ли роли найдены
    missing_roles = set(data.role_ids) - roles_map.keys()
    if missing_roles:
        raise GraphQLError(f"Роли с ID не найдены: {', '.join(map(str, missing_roles))}")
    
    # === Собираем все уникальные права из всех ролей (right_id, goal_id) ===
    role_rights_result = await session.execute(
        select(RoleRightGoal).where(
            RoleRightGoal.role_id.in_(roles_map.keys())
        )
    )
    role_rights = role_rights_result.scalars().all()
    
    # Собираем уникальные права из всех ролей
    required_permissions_set = set()
    for rrg in role_rights:
        required_permissions_set.add((rrg.right_id, rrg.goal_id))
    
    # Конвертируем set в list для передачи в функцию валидации
    required_permissions = list(required_permissions_set)
    
    # === Проверяем права пользователя через единую функцию ===
    missing = await service.check_grant_permissions(
        current_user.id,
        required_permissions
    )
    
    if missing:
        raise GraphQLError(
            f"Недостаточно прав для назначения ролей. Обнаружена попытка эскалации привилегий. "
            f"У вас нет следующих прав, которые присутствуют в назначаемых ролях: "
            f"{', '.join(missing)}. "
            f"Вы можете назначать только те роли, права которых не превышают ваши собственные."
        )
    
    # === Назначаем роли (избегаем дубликатов) ===
    assigned_count = 0
    skipped_count = 0
    
    for role_id in data.role_ids:
        # Проверяем, не назначена ли уже эта роль
        existing_assignment = (
            await session.execute(
                select(UserRole).where(
                    UserRole.user_id == data.user_id,
                    UserRole.role_id == role_id
                )
            )
        ).scalars().first()
        
        if existing_assignment:
            skipped_count += 1
            continue
        
        # Создаем связь
        user_role = UserRole(user_id=data.user_id, role_id=role_id)
        session.add(user_role)
        assigned_count += 1
    
    await session.commit()
    
    # Перезагружаем пользователя с ролями для возврата полных данных
    statement = (
        select(User)
        .options(
            selectinload(User.user_roles)
            .selectinload(UserRole.role)
        )
        .where(User.id == data.user_id)
    )
    
    user_with_roles = (await session.execute(statement)).scalars().first()
    
    from .user import _to_user
    
    message = f"Успешно назначено ролей: {assigned_count}"
    if skipped_count > 0:
        message += f" (пропущено уже назначенных: {skipped_count})"
    
    return GrantRoleResult(
        success=True,
        message=message,
        user=_to_user(user_with_roles)
    )


async def revoke_role(
    info: Info,
    user_id: int,
    role_id: int
) -> GrantRoleResult:
    """Мутация для отзыва роли у пользователя.
    
    ВАЖНО:
    Нельзя отозвать роль, если у пользователя нет соответствующих прав с can_grant = True, которые содержатся в этой роли.
    (защита от злоупотреблений)
    """
    
    session: AsyncSession = info.context["db"]
    current_user = info.context["current_user"]
    service: PermissionService = info.context["permission_service"]
    
    # Проверяем существование связи
    user_role = (
        await session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        )
    ).scalars().first()

    if not user_role:
        raise GraphQLError(f"Связь пользователь-роль не найдена (user_id={user_id}, role_id={role_id})")

    # === Проверяем права на эскалацию (аналогично grant_role) ===
    role_rights_result = await session.execute(
        select(RoleRightGoal).where(RoleRightGoal.role_id == role_id)
    )
    role_rights = role_rights_result.scalars().all()

    required_permissions_set = set()
    for rrg in role_rights:
        required_permissions_set.add((rrg.right_id, rrg.goal_id))

    required_permissions = list(required_permissions_set)

    missing = await service.check_grant_permissions(
        current_user.id,
        required_permissions
    )

    if missing:
        raise GraphQLError(
            f"Невозможно отозвать роль. У вас нет следующих прав, которые присутствуют в этой роли: "
            f"{', '.join(missing)}. "
            f"Вы можете отзывать только те роли, права которых не превышают ваши собственные."
        )
    
    # === Отзыв роли ===
    await session.delete(user_role)
    await session.commit()
    
    # Перезагружаем пользователя с ролями
    statement = (
        select(User)
        .options(
            selectinload(User.user_roles)
            .selectinload(UserRole.role)
        )
        .where(User.id == user_id)
    )
    
    user_with_roles = (await session.execute(statement)).scalars().first()
    
    from .user import _to_user
    
    return GrantRoleResult(
        success=True,
        message=f"Роль {role_id} успешно отозвана у пользователя {user_id}",
        user=_to_user(user_with_roles) if user_with_roles else None
    )
