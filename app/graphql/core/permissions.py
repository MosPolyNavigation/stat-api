from enum import IntEnum
from dataclasses import dataclass
from typing import Sequence, Optional
from functools import wraps
from graphql import GraphQLError
from strawberry.types import Info

from app.constants import (
    VIEW_RIGHT_ID, CREATE_RIGHT_ID, EDIT_RIGHT_ID, DELETE_RIGHT_ID,
    STATS_GOAL_ID, DASHBOARDS_GOAL_ID, USERS_GOAL_ID, ROLES_GOAL_ID,
    TABLES_GOAL_ID, RESOURCES_GOAL_ID, TASKS_GOAL_ID, NAV_GOAL_ID,
    USER_PASS_GOAL_ID, ADMIN_GOAL_ID, REVIEWS_GOAL_ID,
    REFRESH_TOKEN_GOAL_ID, CLIENT_GOAL_ID, GOAL_RIGHTS
)
from app.graphql.core.context import GraphQLContext


# =============================================================================
# 1. Типобезопасные Enums (значения точно совпадают с ID в БД)
# =============================================================================
class Right(IntEnum):
    VIEW = VIEW_RIGHT_ID
    CREATE = CREATE_RIGHT_ID
    EDIT = EDIT_RIGHT_ID
    DELETE = DELETE_RIGHT_ID


class Goal(IntEnum):
    STATS = STATS_GOAL_ID
    DASHBOARDS = DASHBOARDS_GOAL_ID
    USERS = USERS_GOAL_ID
    ROLES = ROLES_GOAL_ID
    TABLES = TABLES_GOAL_ID
    RESOURCES = RESOURCES_GOAL_ID
    TASKS = TASKS_GOAL_ID
    NAV_DATA = NAV_GOAL_ID
    USER_PASS = USER_PASS_GOAL_ID
    ADMIN = ADMIN_GOAL_ID
    REVIEWS = REVIEWS_GOAL_ID
    REFRESH_TOKEN = REFRESH_TOKEN_GOAL_ID
    CLIENT = CLIENT_GOAL_ID


# =============================================================================
# 2. Единица проверки # app/graphql/core/permissions.py+ валидация комбинаций
# =============================================================================
@dataclass(frozen=True)
class Permission:
    right: Right
    goal: Goal

    def __post_init__(self):
        # Защищаемся от невозможных комбинаций на уровне инициализации
        if (self.goal, self.right) not in GOAL_RIGHTS:
            raise ValueError(
                f"Недопустимая комбинация права и цели: {self.right.name} -> {self.goal.name}"
            )

    def __repr__(self) -> str:
        return f"{self.right.name.lower()}:{self.goal.name.lower()}"

    def __hash__(self) -> int:
        return hash((self.right, self.goal))


# =============================================================================
# 3. Предустановленные права (удобный namespace)
# =============================================================================
class P:
    # Stats (1)
    STATS_VIEW = Permission(Right.VIEW, Goal.STATS)
    STATS_CREATE = Permission(Right.CREATE, Goal.STATS)
    STATS_EDIT = Permission(Right.EDIT, Goal.STATS)
    STATS_DELETE = Permission(Right.DELETE, Goal.STATS)

    # Dashboards (2)
    DASHBOARDS_VIEW = Permission(Right.VIEW, Goal.DASHBOARDS)
    DASHBOARDS_CREATE = Permission(Right.CREATE, Goal.DASHBOARDS)
    DASHBOARDS_EDIT = Permission(Right.EDIT, Goal.DASHBOARDS)
    DASHBOARDS_DELETE = Permission(Right.DELETE, Goal.DASHBOARDS)

    # Users (3)
    USERS_VIEW = Permission(Right.VIEW, Goal.USERS)
    USERS_CREATE = Permission(Right.CREATE, Goal.USERS)
    USERS_EDIT = Permission(Right.EDIT, Goal.USERS)
    USERS_DELETE = Permission(Right.DELETE, Goal.USERS)

    # Roles (4)
    ROLES_VIEW = Permission(Right.VIEW, Goal.ROLES)
    ROLES_CREATE = Permission(Right.CREATE, Goal.ROLES)
    ROLES_EDIT = Permission(Right.EDIT, Goal.ROLES)
    ROLES_DELETE = Permission(Right.DELETE, Goal.ROLES)

    # Tables (5)
    TABLES_VIEW = Permission(Right.VIEW, Goal.TABLES)
    TABLES_EDIT = Permission(Right.EDIT, Goal.TABLES)

    # Resources (6)
    RESOURCES_VIEW = Permission(Right.VIEW, Goal.RESOURCES)
    RESOURCES_CREATE = Permission(Right.CREATE, Goal.RESOURCES)
    RESOURCES_EDIT = Permission(Right.EDIT, Goal.RESOURCES)
    RESOURCES_DELETE = Permission(Right.DELETE, Goal.RESOURCES)

    # Tasks (7)
    TASKS_VIEW = Permission(Right.VIEW, Goal.TASKS)
    TASKS_CREATE = Permission(Right.CREATE, Goal.TASKS)
    TASKS_EDIT = Permission(Right.EDIT, Goal.TASKS)
    TASKS_DELETE = Permission(Right.DELETE, Goal.TASKS)

    # Nav Data (8)
    NAV_VIEW = Permission(Right.VIEW, Goal.NAV_DATA)
    NAV_CREATE = Permission(Right.CREATE, Goal.NAV_DATA)
    NAV_EDIT = Permission(Right.EDIT, Goal.NAV_DATA)
    NAV_DELETE = Permission(Right.DELETE, Goal.NAV_DATA)

    # User Pass (9)
    USER_PASS_EDIT = Permission(Right.EDIT, Goal.USER_PASS)

    # Admin (10)
    ADMIN_VIEW = Permission(Right.VIEW, Goal.ADMIN)
    ADMIN_EDIT = Permission(Right.EDIT, Goal.ADMIN)

    # Reviews (11)
    REVIEWS_VIEW = Permission(Right.VIEW, Goal.REVIEWS)
    REVIEWS_EDIT = Permission(Right.EDIT, Goal.REVIEWS)

    # Refresh Token (12)
    REFRESH_TOKEN_VIEW = Permission(Right.VIEW, Goal.REFRESH_TOKEN)
    REFRESH_TOKEN_EDIT = Permission(Right.EDIT, Goal.REFRESH_TOKEN)
    REFRESH_TOKEN_DELETE = Permission(Right.DELETE, Goal.REFRESH_TOKEN)

    # Client (13)
    CLIENT_CREATE = Permission(Right.CREATE, Goal.CLIENT)
    # ... добавляйте по необходимости


async def _get_missing_permissions(
        info: Info, permissions: Sequence[Permission]
) -> Optional[Sequence[Permission]]:
    """Внутренняя функция: возвращает список отсутствующих прав."""
    ctx: GraphQLContext = info.context
    # Ожидается, что сервис возвращает set[(right_id, goal_id)]
    user_perms = await ctx.permission_service.get_user_permissions(ctx.current_user.id)

    missing = [p for p in permissions if (p.right, p.goal) not in user_perms]
    return missing if missing else None


async def require_permissions(info: Info, *permissions: Permission) -> None:
    """
    Guard-функция: проверяет права и бросает GraphQLError при отсутствии.
    ✅ Идеально для async-резолверов и Relay connections.
    """
    missing = await _get_missing_permissions(info, permissions)
    if missing:
        names = ", ".join(repr(p) for p in missing)
        raise GraphQLError(f"Недостаточно прав для выполнения операции. Отсутствуют: {names}")


def check_permissions(*permissions: Permission):
    """
    Декоратор для автоматической проверки прав перед выполнением резолвера.
    Работает с @strawberry.field и @relay.connection.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Извлекаем info из kwargs (Strawberry передаёт его именованным)
            info = kwargs.get("info")
            if info is None or not isinstance(info, Info):
                # Фоллбэк на позиционный аргумент (если резолвер написан нестандартно)
                info = next((a for a in args if isinstance(a, Info)), None)

            if info is None:
                raise GraphQLError("Internal error: контекст Info не найден для проверки прав")

            await require_permissions(info, *permissions)
            return await func(*args, **kwargs)

        return wrapper

    return decorator
