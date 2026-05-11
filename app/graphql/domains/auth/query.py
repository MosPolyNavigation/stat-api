from typing import Optional
import strawberry
from strawberry import Info
from sqlalchemy import select

from app.graphql.core.pagination import paginate_query, PaginationInput, Connection, pagination_input_from_attrs
from app.graphql.core.filters import apply_filters
from app.graphql.core.ordering import apply_order_by
from app.graphql.core.resource_factory import create_query_resource
from app.graphql.core.permissions import require_permissions, P
from app.graphql.core.context import GraphQLContext

from app.graphql.domains.auth.resources import (
    UserResource, RoleResource, RightResource, GoalResource,
    RefreshTokenResource, UserLogResource
)
from app.graphql.domains.auth.types import (
    UserRole as UserRoleType,
    RoleRightGoal as RoleRightGoalType,
    _user_role_from_model,
    _role_right_goal_from_model
)
from app.graphql.domains.auth.inputs import (
    UserRoleFilterInput,
    UserRoleOrderByInput,
    RoleRightGoalFilterInput,
    RoleRightGoalOrderByInput
)
from app.models.auth.user_role import UserRole
from app.models.auth.role_right_goal import RoleRightGoal

# =============================================================================
# Фабричные запросы
# =============================================================================
UserQuery = create_query_resource(
    UserResource,
    name_list="users",
    name_get="user"
)

RoleQuery = create_query_resource(
    RoleResource,
    name_list="roles",
    name_get="role"
)

RightQuery = create_query_resource(
    RightResource,
    name_list="rights",
    name_get="right"
)

GoalQuery = create_query_resource(
    GoalResource,
    name_list="goals",
    name_get="goal"
)

RefreshTokenQuery = create_query_resource(
    RefreshTokenResource,
    name_list="refresh_tokens",
    name_get="refresh_token"
)

UserLogQuery = create_query_resource(
    UserLogResource,
    name_list="user_logs",
    name_get="user_log"
)


# =============================================================================
# Кастомные запросы для Join-таблиц
# =============================================================================
@strawberry.type
class UserRoleQuery:
    @strawberry.field()
    async def user_roles(
        self,
        info: Info,
        pagination: Optional[PaginationInput] = None,
        filter: Optional[UserRoleFilterInput] = None,
        order_by: Optional[UserRoleOrderByInput] = None,
    ) -> Connection[UserRoleType]:
        await require_permissions(info, P.ROLES_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(UserRole)
        if filter:
            stmt = apply_filters(stmt, UserRole, filter)
        if order_by:
            stmt = apply_order_by(stmt, UserRole, order_by)

        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)

        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_user_role_from_model,
        )

    @strawberry.field()
    async def user_role(self, info: Info, user_id: int, role_id: int) -> Optional[UserRoleType]:
        await require_permissions(info, P.ROLES_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        model = (await ctx.db.execute(stmt)).scalar_one_or_none()

        return _user_role_from_model(model) if model else None


@strawberry.type
class RoleRightGoalQuery:
    @strawberry.field()
    async def role_right_goals(
            self,
            info: Info,
            pagination: Optional[PaginationInput] = None,
            filter: Optional[RoleRightGoalFilterInput] = None,
            order_by: Optional[RoleRightGoalOrderByInput] = None,
    ) -> Connection[RoleRightGoalType]:
        await require_permissions(info, P.ROLES_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(RoleRightGoal)
        if filter:
            stmt = apply_filters(stmt, RoleRightGoal, filter)
        if order_by:
            stmt = apply_order_by(stmt, RoleRightGoal, order_by)

        if pagination is None:
            pagination = pagination_input_from_attrs(page=1, page_size=10)

        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_role_right_goal_from_model,
        )

    @strawberry.field()
    async def role_right_goal(
        self, info: Info, role_id: int, right_id: int, goal_id: int
    ) -> Optional[RoleRightGoalType]:
        await require_permissions(info, P.ROLES_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(RoleRightGoal).where(
            RoleRightGoal.role_id == role_id,
            RoleRightGoal.right_id == right_id,
            RoleRightGoal.goal_id == goal_id,
        )
        model = (await ctx.db.execute(stmt)).scalar_one_or_none()

        return _role_right_goal_from_model(model) if model else None


# =============================================================================
# Корневой Query
# =============================================================================
@strawberry.type
class Query(
    UserQuery,
    RoleQuery,
    RightQuery,
    GoalQuery,
    RefreshTokenQuery,
    UserLogQuery,
    UserRoleQuery,
    RoleRightGoalQuery,
):
    """Корневой Query для домена auth."""
    pass
