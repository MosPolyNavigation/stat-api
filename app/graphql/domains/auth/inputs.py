import strawberry
from typing import Optional, List
from app.graphql.core.filters import (
    BaseFilterInput,
    IntFilterInput,
    BooleanFilterInput,
    StringFilterInput,
)
from app.graphql.core.ordering import OrderDir, BaseOrderByInput


# =============================================================================
# Filters
# =============================================================================
@strawberry.input
class UserFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    login: Optional[StringFilterInput] = None
    fio: Optional[StringFilterInput] = None
    is_active: Optional[BooleanFilterInput] = None
    and_: Optional[List["UserFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["UserFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["UserFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class RoleFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    and_: Optional[List["RoleFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["RoleFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["RoleFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class UserRoleFilterInput(BaseFilterInput):
    user_id: Optional[IntFilterInput] = None
    role_id: Optional[IntFilterInput] = None
    and_: Optional[List["UserRoleFilterInput"]] = strawberry.field(
        name="and", default=None
    )
    or_: Optional[List["UserRoleFilterInput"]] = strawberry.field(
        name="or", default=None
    )
    not_: Optional["UserRoleFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class RoleRightGoalFilterInput(BaseFilterInput):
    role_id: Optional[IntFilterInput] = None
    right_id: Optional[IntFilterInput] = None
    goal_id: Optional[IntFilterInput] = None
    can_grant: Optional[BooleanFilterInput] = None
    and_: Optional[List["RoleRightGoalFilterInput"]] = strawberry.field(
        name="and", default=None
    )
    or_: Optional[List["RoleRightGoalFilterInput"]] = strawberry.field(
        name="or", default=None
    )
    not_: Optional["RoleRightGoalFilterInput"] = strawberry.field(
        name="not", default=None
    )


@strawberry.input
class RightFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    and_: Optional[List["RightFilterInput"]] = strawberry.field(
        name="and", default=None
    )
    or_: Optional[List["RightFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["RightFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class GoalFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    and_: Optional[List["GoalFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["GoalFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["GoalFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class RefreshTokenFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    user_id: Optional[IntFilterInput] = None
    jti: Optional[StringFilterInput] = None
    browser: Optional[StringFilterInput] = None
    user_ip: Optional[StringFilterInput] = None
    revoked: Optional[BooleanFilterInput] = None
    and_: Optional[List["RefreshTokenFilterInput"]] = strawberry.field(
        name="and", default=None
    )
    or_: Optional[List["RefreshTokenFilterInput"]] = strawberry.field(
        name="or", default=None
    )
    not_: Optional["RefreshTokenFilterInput"] = strawberry.field(
        name="not", default=None
    )


@strawberry.input
class UserLogFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    user_id: Optional[IntFilterInput] = None
    text: Optional[StringFilterInput] = None
    and_: Optional[List["UserLogFilterInput"]] = strawberry.field(
        name="and", default=None
    )
    or_: Optional[List["UserLogFilterInput"]] = strawberry.field(
        name="or", default=None
    )
    not_: Optional["UserLogFilterInput"] = strawberry.field(name="not", default=None)


# =============================================================================
# OrderBy
# =============================================================================
@strawberry.input
class UserOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    login: Optional[OrderDir] = None
    fio: Optional[OrderDir] = None
    is_active: Optional[OrderDir] = None
    registration_date: Optional[OrderDir] = None
    updated_at: Optional[OrderDir] = None
    then_by: Optional["UserOrderByInput"] = None


@strawberry.input
class RoleOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["RoleOrderByInput"] = None


@strawberry.input
class UserRoleOrderByInput(BaseOrderByInput):
    user_id: Optional[OrderDir] = None
    role_id: Optional[OrderDir] = None
    then_by: Optional["UserRoleOrderByInput"] = None


@strawberry.input
class RoleRightGoalOrderByInput(BaseOrderByInput):
    role_id: Optional[OrderDir] = None
    right_id: Optional[OrderDir] = None
    goal_id: Optional[OrderDir] = None
    can_grant: Optional[OrderDir] = None
    then_by: Optional["RoleRightGoalOrderByInput"] = None


@strawberry.input
class RightOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["RightOrderByInput"] = None


@strawberry.input
class GoalOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["GoalOrderByInput"] = None


@strawberry.input
class RefreshTokenOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    user_id: Optional[OrderDir] = None
    jti: Optional[OrderDir] = None
    exp_date: Optional[OrderDir] = None
    browser: Optional[OrderDir] = None
    user_ip: Optional[OrderDir] = None
    revoked: Optional[OrderDir] = None
    created_at: Optional[OrderDir] = None
    then_by: Optional["RefreshTokenOrderByInput"] = None


@strawberry.input
class UserLogOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    user_id: Optional[OrderDir] = None
    text: Optional[OrderDir] = None
    created_at: Optional[OrderDir] = None
    then_by: Optional["UserLogOrderByInput"] = None


# =============================================================================
# Mutation Inputs
# =============================================================================
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
    can_grant: bool = False


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


@strawberry.input
class UpdateUserInput:
    """Входные данные для редактирования пользователя."""

    fio: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class UpdateRoleInput:
    """Входные данные для редактирования роли."""

    name: Optional[str] = None
    role_right_goals: Optional[List[RoleRightGoalInput]] = None


@strawberry.input
class ChangeUserPasswordInput:
    """Входные данные для смены пароля пользователя."""

    user_id: int
    new_password: str
