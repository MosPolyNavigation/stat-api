from typing import Tuple
from graphql import GraphQLError
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
