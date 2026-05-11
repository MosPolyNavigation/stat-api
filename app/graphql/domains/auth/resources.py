from app.graphql.core.resource import ResourceConfig, ResourcePermissions
from app.graphql.core.permissions import P
from app.models.auth.user import User as UserModel
from app.models.auth.role import Role as RoleModel
from app.models.auth.right import Right as RightModel
from app.models.auth.goal import Goal as GoalModel
from app.models.auth.refresh_token import RefreshToken as RTModel
from app.models.auth.user_log import UserLog as ULModel
from app.graphql.domains.auth.types import (
    User as UserType,
    Role as RoleType,
    Right as RightType,
    Goal as GoalType,
    RefreshToken as RefreshTokenType,
    UserLog as UserLogType,
    _user_from_model,
    _role_from_model,
    _right_from_model,
    _goal_from_model,
    _refresh_token_from_model,
    _user_log_from_model
)
from app.graphql.domains.auth.inputs import (
    UserFilterInput,
    UserOrderByInput,
    RoleFilterInput,
    RoleOrderByInput,
    RightFilterInput,
    RightOrderByInput,
    GoalFilterInput,
    GoalOrderByInput,
    RefreshTokenFilterInput,
    RefreshTokenOrderByInput,
    UserLogFilterInput,
    UserLogOrderByInput
)

UserResource = ResourceConfig(
    model=UserModel,
    graphql_type=UserType,
    filter_input=UserFilterInput,
    order_by_input=UserOrderByInput,
    convert=_user_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.USERS_VIEW,
        create=P.USERS_CREATE,
        edit=P.USERS_EDIT,
        delete=P.USERS_DELETE
    ),
    enable_logging=True,
    enable_logging_list=False
)

RoleResource = ResourceConfig(
    model=RoleModel,
    graphql_type=RoleType,
    filter_input=RoleFilterInput,
    order_by_input=RoleOrderByInput,
    convert=_role_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.ROLES_VIEW,
        create=P.ROLES_CREATE,
        edit=P.ROLES_EDIT,
        delete=P.ROLES_DELETE
    ),
    enable_logging=True,
    enable_logging_list=False
)

RightResource = ResourceConfig(
    model=RightModel,
    graphql_type=RightType,
    filter_input=RightFilterInput,
    order_by_input=RightOrderByInput,
    convert=_right_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(view=P.ROLES_VIEW)
)

GoalResource = ResourceConfig(
    model=GoalModel,
    graphql_type=GoalType,
    filter_input=GoalFilterInput,
    order_by_input=GoalOrderByInput,
    convert=_goal_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(view=P.ROLES_VIEW)
)

RefreshTokenResource = ResourceConfig(
    model=RTModel,
    graphql_type=RefreshTokenType,
    filter_input=RefreshTokenFilterInput,
    order_by_input=RefreshTokenOrderByInput,
    convert=_refresh_token_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(view=P.REFRESH_TOKEN_VIEW),
)

UserLogResource = ResourceConfig(
    model=ULModel,
    graphql_type=UserLogType,
    filter_input=UserLogFilterInput,
    order_by_input=UserLogOrderByInput,
    convert=_user_log_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(view=P.ADMIN_VIEW),
)
