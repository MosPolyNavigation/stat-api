from typing import Tuple, List, Optional
from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info
from app.models import User
from app.constants import (
    # Goals
    STATS_GOAL_ID,
    DASHBOARDS_GOAL_ID,
    USERS_GOAL_ID,
    ROLES_GOAL_ID,
    TABLES_GOAL_ID,
    RESOURCES_GOAL_ID,
    TASKS_GOAL_ID,
    NAV_GOAL_ID,
    USER_PASS_GOAL_ID,
    REVIEWS_GOAL_ID,
    # Rights
    VIEW_RIGHT_ID,
    CREATE_RIGHT_ID,
    EDIT_RIGHT_ID,
    DELETE_RIGHT_ID,
    GRANT_RIGHT_ID,
    # Hashmaps
    RIGHTS_BY_NAME,
    RIGHTS_BY_ID,
    GOALS_BY_ID
)
from app.services.permission_service import PermissionService


def _get_session_user_and_service(info: Info) -> Tuple[AsyncSession, User, PermissionService]:
    try:
        session: AsyncSession = info.context["db"]
        current_user: User = info.context["current_user"]
        permission_service: PermissionService = info.context["permission_service"]
    except KeyError as exc:
        raise GraphQLError("В контексте GraphQL отсутствуют необходимые значения") from exc
    return session, current_user, permission_service


async def validate_user_permissions_by_ids(
    user_id: int,
    service: PermissionService,
    required_permissions: List[Tuple[int, int]]
) -> Optional[List[str]]:
    """
    Проверяет, есть ли у пользователя все требуемые права (по ID).
    
    Args:
        user: Текущий пользователь
        service: Сервис проверки прав
        required_permissions: Список кортежей (right_id, goal_id)
                              Пример: [(1, 3), (2, 1)] где 1=view, 3=users
    
    Returns:
        Список отсутствующих прав в формате ["right -> goal", ...]
        Если все права есть — возвращает None
    """
    from app.models import Right, Goal
    if not required_permissions:
        return None

    user_rights = await service.get_user_permissions(user_id)
    
    missing = []
    for right_id, goal_id in required_permissions:
        right_name = RIGHTS_BY_ID.get(right_id)
        goal_name = GOALS_BY_ID.get(goal_id)

        if right_name is None or goal_name is None:
            unknown = []
            if right_name is None:
                unknown.append(f"right_id={right_id}")
            if goal_name is None:
                unknown.append(f"goal_id={goal_id}")
            raise GraphQLError(f"Неизвестный идентификатор права/цели: {', '.join(unknown)}")
        
        if (right_id, goal_id) not in user_rights:
            missing.append(f"{right_name} -> {goal_name}")
    
    return missing if missing else None


async def ensure_permissions_by_ids(
    info: Info,
    required_permissions: List[Tuple[int, int]],
    error_message: str = "Недостаточно прав для выполнения операции"
) -> AsyncSession:
    session, current_user, service = _get_session_user_and_service(info)
    
    missing = await validate_user_permissions_by_ids(current_user.id, service, required_permissions)
    
    if missing:
        full_message = (
            f"{error_message}. "
            f"Отсутствуют следующие права: {', '.join(missing)}. "
            f"Вы можете выполнять только те действия, на которые у вас есть права."
        )
        raise GraphQLError(full_message)
    
    return session


async def validate_role_right_goals_duplicates(
    role_right_goals: List
) -> None:
    """
    Проверяет список RoleRightGoalInput на дублирующиеся связи (right_id, goal_id).
    
    Args:
        role_right_goals: Список объектов с полями right_id и goal_id
    
    Raises:
        GraphQLError: Если найдены дублирующиеся связи
    """
    if not role_right_goals:
        return
    
    seen_combinations = set()
    duplicates = []
    
    for rrg_input in role_right_goals:
        combination_key = (rrg_input.right_id, rrg_input.goal_id)
        if combination_key in seen_combinations:
            duplicates.append(combination_key)
        seen_combinations.add(combination_key)
    
    # 2. Если есть дубликаты — формируем сообщение из констант (без БД!)
    if duplicates:
        duplicate_messages = [
            f"{RIGHTS_BY_ID.get(right_id, f'right:{right_id}')} -> "
            f"{GOALS_BY_ID.get(goal_id, f'goal:{goal_id}')}"
            for right_id, goal_id in duplicates
        ]
        
        raise GraphQLError(f"Дублирующиеся связи: {', '.join(duplicate_messages)}")


async def ensure_stats_view_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(VIEW_RIGHT_ID, STATS_GOAL_ID)], "Недостаточно прав для просмотра статистики"
    )


async def ensure_stats_create_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(CREATE_RIGHT_ID, STATS_GOAL_ID)], "Недостаточно прав для создания справочников статистики"
    )


async def ensure_stats_edit_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(EDIT_RIGHT_ID, STATS_GOAL_ID)], "Недостаточно прав для редактирования справочников статистики"
    )


async def ensure_stats_delete_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(DELETE_RIGHT_ID, STATS_GOAL_ID)], "Недостаточно прав для удаления справочников статистики"
    )


async def ensure_reviews_view_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(VIEW_RIGHT_ID, REVIEWS_GOAL_ID)], "Недостаточно прав для просмотра статистики"
    )


async def _ensure_nav_permission(info: Info, right_id: int) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(right_id, NAV_GOAL_ID)], f"Недостаточно прав для работы с навигацией"
    )

async def ensure_nav_permission(info: Info, right_name: str) -> AsyncSession:
    right_id = RIGHTS_BY_NAME.get(right_name)
    return await _ensure_nav_permission(info, right_id)


async def ensure_users_view_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(VIEW_RIGHT_ID, USERS_GOAL_ID)], "Недостаточно прав для просмотра пользователей"
    )


async def ensure_users_create_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(CREATE_RIGHT_ID, USERS_GOAL_ID)], "Недостаточно прав для создания пользователей"
    )


async def ensure_users_edit_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(EDIT_RIGHT_ID, USERS_GOAL_ID)], "Недостаточно прав для редактирования пользователей"
    )


async def ensure_users_delete_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(DELETE_RIGHT_ID, USERS_GOAL_ID)], "Недостаточно прав для удаления пользователей"
    )


async def ensure_user_pass_edit_permission(info: Info) -> AsyncSession:
    """Проверка права на редактирование пароля пользователя (user_pass -> edit)."""
    return await ensure_permissions_by_ids(
        info, [(EDIT_RIGHT_ID, USER_PASS_GOAL_ID)], "Недостаточно прав для смены пароля пользователя"
    )


async def ensure_roles_view_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(VIEW_RIGHT_ID, ROLES_GOAL_ID)], "Недостаточно прав для просмотра ролей"
    )


async def ensure_roles_create_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(CREATE_RIGHT_ID, ROLES_GOAL_ID)], "Недостаточно прав для создания ролей"
    )


async def ensure_roles_edit_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(EDIT_RIGHT_ID, ROLES_GOAL_ID)], "Недостаточно прав для редактирования ролей"
    )


async def ensure_roles_delete_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(DELETE_RIGHT_ID, ROLES_GOAL_ID)], "Недостаточно прав для удаления ролей"
    )


async def ensure_roles_grant_permission(info: Info) -> AsyncSession:
    return await ensure_permissions_by_ids(
        info, [(GRANT_RIGHT_ID, ROLES_GOAL_ID)], "Недостаточно прав для выдачи ролей"
    )
