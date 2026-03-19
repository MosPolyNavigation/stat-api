from typing import Tuple, List, Optional
from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info
from app.models import User

STATS_GOAL_NAME = "stats"
NAV_GOAL_NAME = "nav_data"
USERS_GOAL_NAME = "users"
ROLES_GOAL_NAME = "roles"

VIEW_RIGHT_NAME = "view"
CREATE_RIGHT_NAME = "create"
EDIT_RIGHT_NAME = "edit"
DELETE_RIGHT_NAME = "delete"
GRANT_RIGHT_NAME = "grant"


def _get_session_and_user(info: Info) -> Tuple[AsyncSession, User]:
    try:
        session: AsyncSession = info.context["db"]
        current_user: User = info.context["current_user"]
    except KeyError as exc:
        raise GraphQLError("В контексте GraphQL отсутствуют необходимые значения") from exc
    return session, current_user


async def ensure_stats_view_permission(info: Info) -> AsyncSession:
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, STATS_GOAL_NAME, VIEW_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для просмотра статистики")
    return session


async def ensure_nav_permission(info: Info, right: str) -> AsyncSession:
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, NAV_GOAL_NAME, right):
        raise GraphQLError("Недостаточно прав для работы с навигацией")
    return session


async def ensure_users_view_permission(info: Info) -> AsyncSession:
    """Проверка права на просмотр пользователей (users -> view)."""
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, USERS_GOAL_NAME, VIEW_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для просмотра пользователей")
    return session


async def ensure_users_create_permission(info: Info) -> AsyncSession:
    """Проверка права на создание пользователей (users -> create)."""
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, USERS_GOAL_NAME, CREATE_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для создания пользователей")
    return session


async def ensure_roles_view_permission(info: Info) -> AsyncSession:
    """Проверка права на просмотр ролей и связанных таблиц (roles -> view)."""
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, ROLES_GOAL_NAME, VIEW_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для просмотра ролей")
    return session


async def ensure_roles_create_permission(info: Info) -> AsyncSession:
    """Проверка права на редактирование ролей (roles -> create)."""
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, ROLES_GOAL_NAME, CREATE_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для редактирования ролей")
    return session


async def ensure_roles_edit_permission(info: Info) -> AsyncSession:
    """Проверка права на редактирование ролей (roles -> edit)."""
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, ROLES_GOAL_NAME, EDIT_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для редактирования ролей")
    return session


async def ensure_roles_grant_permission(info: Info) -> AsyncSession:
    """Проверка права на выдачу прав (roles -> grant)."""
    session, current_user = _get_session_and_user(info)
    if not await current_user.is_capable(session, ROLES_GOAL_NAME, GRANT_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для выдачи прав")
    return session


async def validate_user_permissions_by_ids(
    user: User,
    session: AsyncSession,
    required_permissions: List[Tuple[int, int]]  # [(right_id, goal_id), ...]
) -> Optional[List[str]]:
    """
    Проверяет, есть ли у пользователя все требуемые права (по ID).
    
    Args:
        user: Текущий пользователь
        session: Сессия базы данных
        required_permissions: Список кортежей (right_id, goal_id)
                              Пример: [(1, 3), (2, 1)] где 1=view, 3=users
    
    Returns:
        Список отсутствующих прав в формате ["right -> goal", ...]
        Если все права есть — возвращает None
    """
    from app.models import Right, Goal
    if not required_permissions:
        return None
    
    # Собираем уникальные ID для bulk-запроса
    unique_right_ids = {right_id for right_id, _ in required_permissions}
    unique_goal_ids = {goal_id for _, goal_id in required_permissions}
    
    # Один запрос для всех прав
    rights_result = await session.execute(
        select(Right).where(Right.id.in_(unique_right_ids))
    )
    rights_map = {right.id: right.name for right in rights_result.scalars().all()}
    
    # Один запрос для всех целей
    goals_result = await session.execute(
        select(Goal).where(Goal.id.in_(unique_goal_ids))
    )
    goals_map = {goal.id: goal.name for goal in goals_result.scalars().all()}
    
    # Проверяем, все ли ID найдены
    missing_right_ids = unique_right_ids - rights_map.keys()
    missing_goal_ids = unique_goal_ids - goals_map.keys()
    
    if missing_right_ids:
        raise GraphQLError(f"Права с ID не найдены: {', '.join(map(str, missing_right_ids))}")
    if missing_goal_ids:
        raise GraphQLError(f"Цели с ID не найдены: {', '.join(map(str, missing_goal_ids))}")
    
    # Получаем права пользователя
    user_rights = await user.get_rights(session)
    # Формат: {"users": ["view", "create"], "roles": ["view"], ...}
    
    missing = []
    for right_id, goal_id in required_permissions:
        right_name = rights_map[right_id]
        goal_name = goals_map[goal_id]
        
        goal_rights = user_rights.get(goal_name, [])
        if right_name not in goal_rights:
            missing.append(f"{right_name} -> {goal_name}")
    
    return missing if missing else None
