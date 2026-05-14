from typing import Optional
from datetime import datetime
import strawberry

from app.graphql.core.context import GraphQLContext
from app.graphql.core.list_ops import process_list
from app.graphql.core.pagination import PaginationInput, pagination_input_from_attrs, Connection
from app.graphql.core.permissions import require_permissions, P
from app.graphql.domains.auth.inputs import (
    RoleRightGoalFilterInput,
    RoleRightGoalOrderByInput,
    UserRoleFilterInput,
    UserRoleOrderByInput,
    RefreshTokenFilterInput,
    RefreshTokenOrderByInput,
    UserLogFilterInput,
    UserLogOrderByInput
)
from app.models import (
    Goal as GoalModel,
    Right as RightModel,
    Role as RoleModel,
    RoleRightGoal as RRGModel,
    UserRole as URModel,
    UserLog as ULModel,
    User as UserModel,
    RefreshToken as RTModel,
)


# =============================================================================
# Helpers: Конвертеры моделей → типы
# =============================================================================
def _goal_from_model(m: GoalModel) -> "Goal":
    return Goal(
        id=m.id,
        name=m.name,
    )


def _right_from_model(m: RightModel) -> "Right":
    return Right(
        id=m.id,
        name=m.name,
    )


def _role_right_goal_from_model(m: RRGModel) -> "RoleRightGoal":
    return RoleRightGoal(
        role_id=m.role_id,
        right_id=m.right_id,
        goal_id=m.goal_id,
        can_grant=m.can_grant,
    )


def _role_from_model(m: RoleModel) -> "Role":
    return Role(
        id=m.id,
        name=m.name,
    )


def _user_role_from_model(m: URModel) -> "UserRole":
    return UserRole(
        user_id=m.user_id,
        role_id=m.role_id,
    )


def _user_from_model(m: UserModel) -> "UserModel":
    return User(
        id=m.id,
        login=m.login,
        fio=m.fio,
        is_active=m.is_active,
        registration_date=m.registration_date,
        updated_at=m.updated_at,
    )


def _refresh_token_from_model(m: RTModel) -> "RefreshToken":
    return RefreshToken(
        id=m.id,
        user_id=m.user_id,
        jti=m.jti,
        exp_date=m.exp_date,
        browser=m.browser,
        user_ip=m.user_ip,
        revoked=m.revoked,
        created_at=m.created_at
    )


def _user_log_from_model(m: ULModel) -> "UserLog":
    return UserLog(
        id=m.id,
        user_id=m.user_id,
        text=m.text,
        created_at=m.created_at,
    )


# =============================================================================
# Типы
# =============================================================================
@strawberry.type
class Goal:
    id: int
    name: str

    @strawberry.field  # type: ignore[unresolved-reference]
    async def role_right_goals(
        self,
        info: strawberry.Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[RoleRightGoalFilterInput] = None,
        order_by: Optional[RoleRightGoalOrderByInput] = None,
    ) -> Connection["RoleRightGoal"]:
        ctx: GraphQLContext = info.context
        rrg_models = await ctx.loaders["role_right_goal_by_goal_id"].load(self.id)
        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)
        return process_list(
            models=rrg_models,
            model_type=RRGModel,
            filters=filter,
            order_by=order_by,
            pagination=pagination,
            convert=_role_right_goal_from_model,
        )


@strawberry.type
class Right:
    id: int
    name: str

    @strawberry.field  # type: ignore[unresolved-reference]
    async def role_right_goals(
        self,
        info: strawberry.Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[RoleRightGoalFilterInput] = None,
        order_by: Optional[RoleRightGoalOrderByInput] = None,
    ) -> Connection["RoleRightGoal"]:
        ctx: GraphQLContext = info.context
        rrg_models = await ctx.loaders["role_right_goal_by_right_id"].load(self.id)
        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)
        return process_list(
            models=rrg_models,
            model_type=RRGModel,
            filters=filter,
            order_by=order_by,
            pagination=pagination,
            convert=_role_right_goal_from_model,
        )


@strawberry.type
class RoleRightGoal:
    """Тип связи роли с правом и целью."""
    role_id: int
    right_id: int
    goal_id: int
    can_grant: bool

    @strawberry.field  # type: ignore[unresolved-reference]
    async def role(self, info: strawberry.Info) -> Optional["Role"]:
        ctx: GraphQLContext = info.context
        role_model = await ctx.loaders["role"].load(self.role_id)
        return _role_from_model(role_model) if role_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def right(self, info: strawberry.Info) -> Optional["Right"]:
        ctx: GraphQLContext = info.context
        right_model = await ctx.loaders["right"].load(self.right_id)
        return _right_from_model(right_model) if right_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def goal(self, info: strawberry.Info) -> Optional["Goal"]:
        ctx: GraphQLContext = info.context
        goal_model = await ctx.loaders["goal"].load(self.goal_id)
        return _goal_from_model(goal_model) if goal_model else None


@strawberry.type
class Role:
    id: int
    name: str

    @strawberry.field  # type: ignore[unresolved-reference]
    async def role_right_goals(
        self,
        info: strawberry.Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[RoleRightGoalFilterInput] = None,
        order_by: Optional[RoleRightGoalOrderByInput] = None,
    ) -> Connection["RoleRightGoal"]:
        ctx: GraphQLContext = info.context
        rrg_models = await ctx.loaders["role_right_goal_by_role_id"].load(self.id)
        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)
        return process_list(
            models=rrg_models,
            model_type=RRGModel,
            filters=filter,
            order_by=order_by,
            pagination=pagination,
            convert=_role_right_goal_from_model,
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def user_roles(
        self,
        info: strawberry.Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[UserRoleFilterInput] = None,
        order_by: Optional[UserRoleOrderByInput] = None,
    ) -> Connection["UserRole"]:
        ctx: GraphQLContext = info.context
        ur_models = await ctx.loaders["user_role_by_role_id"].load(self.id)
        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)
        return process_list(
            models=ur_models,
            model_type=URModel,
            filters=filter,
            order_by=order_by,
            pagination=pagination,
            convert=_user_role_from_model,
        )


@strawberry.type
class User:
    id: int
    login: str
    fio: Optional[str]
    is_active: bool
    registration_date: datetime
    updated_at: datetime

    @strawberry.field  # type: ignore[unresolved-reference]
    async def user_roles(
        self,
        info: strawberry.Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[UserRoleFilterInput] = None,
        order_by: Optional[UserRoleOrderByInput] = None,
    ) -> Connection["UserRole"]:
        await require_permissions(info, P.ROLES_VIEW)
        ctx: GraphQLContext = info.context
        ur_models = await ctx.loaders["user_role_by_user_id"].load(self.id)
        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)
        return process_list(
            models=ur_models,
            model_type=URModel,
            filters=filter,
            order_by=order_by,
            pagination=pagination,
            convert=_user_role_from_model,
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def refresh_tokens(
        self,
        info: strawberry.Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[RefreshTokenFilterInput] = None,
        order_by: Optional[RefreshTokenOrderByInput] = None,
    ) -> Connection["RefreshToken"]:
        ctx: GraphQLContext = info.context
        current_user = info.context.current_user
        if current_user.id != id:
            await require_permissions(info, P.REFRESH_TOKEN_VIEW)
        rt_models = await ctx.loaders["refresh_token_by_user_id"].load(self.id)
        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)
        return process_list(
            models=rt_models,
            model_type=RTModel,
            filters=filter,
            order_by=order_by,
            pagination=pagination,
            convert=_refresh_token_from_model,
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def user_logs(
        self,
        info: strawberry.Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[UserLogFilterInput] = None,
        order_by: Optional[UserLogOrderByInput] = None,
    ) -> Connection["UserLog"]:
        ctx: GraphQLContext = info.context
        ul_models = await ctx.loaders["user_log_by_user_id"].load(self.id)
        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)
        return process_list(
            models=ul_models,
            model_type=ULModel,
            filters=filter,
            order_by=order_by,
            pagination=pagination,
            convert=_user_log_from_model,
        )


@strawberry.type
class UserRole:
    """Тип связи пользователя с ролью."""
    user_id: int
    role_id: int

    @strawberry.field  # type: ignore[unresolved-reference]
    async def user(self, info: strawberry.Info) -> Optional["User"]:
        ctx: GraphQLContext = info.context
        user_model = await ctx.loaders["user"].load(self.user_id)
        return _user_from_model(user_model) if user_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def role(self, info: strawberry.Info) -> Optional["Role"]:
        ctx: GraphQLContext = info.context
        role_model = await ctx.loaders["role"].load(self.role_id)
        return _role_from_model(role_model) if role_model else None


@strawberry.type
class RefreshToken:
    id: int
    user_id: int
    jti: str
    exp_date: datetime
    browser: Optional[str]
    user_ip: Optional[str]
    revoked: bool
    created_at: datetime

    @strawberry.field  # type: ignore[unresolved-reference]
    async def user(self, info: strawberry.Info) -> Optional["User"]:
        ctx: GraphQLContext = info.context
        user_model = await ctx.loaders["user"].load(self.user_id)
        return _user_from_model(user_model) if user_model else None


@strawberry.type
class UserLog:
    id: int
    user_id: int
    text: str
    created_at: datetime

    @strawberry.field  # type: ignore[unresolved-reference]
    async def user(self, info: strawberry.Info) -> Optional["User"]:
        ctx: GraphQLContext = info.context
        user_model = await ctx.loaders["user"].load(self.user_id)
        return _user_from_model(user_model) if user_model else None
