from typing import Optional, List
from datetime import datetime
import strawberry


@strawberry.type
class GoalType:
    id: int
    name: str


@strawberry.type
class RightType:
    id: int
    name: str


@strawberry.type
class RoleRightGoalType:
    """Тип связи роли с правом и целью."""
    role_id: int
    right_id: int
    goal_id: int
    can_grant: bool
    role: Optional["RoleType"] = None
    right: Optional[RightType] = None
    goal: Optional[GoalType] = None


@strawberry.type
class RoleType:
    id: int
    name: str
    role_right_goals: Optional[List[RoleRightGoalType]] = None
    user_roles: Optional[List["UserRoleType"]] = None


@strawberry.type
class UserType:
    id: int
    login: str
    fio: Optional[str]
    is_active: bool
    registration_date: datetime
    updated_at: datetime
    roles: Optional[List["UserRoleType"]] = None


@strawberry.type
class UserRoleType:
    """Тип связи пользователя с ролью."""
    user_id: int
    role_id: int
    user: Optional[UserType] = None
    role: Optional[RoleType] = None


@strawberry.type
class GrantRoleResult:
    """Результат операции назначения роли."""
    success: bool
    message: str
    user: Optional[UserType] = None


@strawberry.type
class DeleteResult:
    """Результат операции удаления."""
    success: bool
    message: str
    deleted_id: Optional[int] = None


@strawberry.type
class ChangePasswordResult:
    """Результат операции смены пароля."""
    success: bool
    message: str
    user_id: Optional[int] = None
