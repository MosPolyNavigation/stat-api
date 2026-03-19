import strawberry
from typing import Optional, List

@strawberry.input
class CreateUserInput:
    """Входные данные для создания пользователя."""
    login: str
    password: str
    fio: Optional[str] = None
    is_active: bool = True


@strawberry.input
class RoleRightGoalInput:
    """Входные данные для связи роли с правом и целью."""
    right_id: int
    goal_id: int


@strawberry.input
class CreateRoleInput:
    """Входные данные для создания роли."""
    name: str
    role_right_goals: Optional[List[RoleRightGoalInput]] = None


@strawberry.input
class GrantRoleInput:
    """Входные данные для назначения роли пользователю."""
    user_id: int
    role_ids: List[int]
