from typing import Optional

import strawberry

from .dod import (
    DodNavAuditoryConnection,
    DodNavAuditoryPhotoConnection,
    DodNavCampusConnection,
    DodNavFloorConnection,
    DodNavLocationConnection,
    DodNavPlanConnection,
    DodNavStaticConnection,
    DodNavTypeConnection,
    resolve_dod_nav_auditories,
    resolve_dod_nav_auditory_photos,
    resolve_dod_nav_campuses,
    resolve_dod_nav_floors,
    resolve_dod_nav_locations,
    resolve_dod_nav_plans,
    resolve_dod_nav_statics,
    resolve_dod_nav_types,
)
from .endpoint_stats import (
    AggregatedEndpointStatisticsType,
    EndpointStatisticsType,
    resolve_endpoint_statistics,
    resolve_endpoint_statistics_avg,
)
from .nav import (
    NavAuditoryConnection,
    NavAuditoryPhotoConnection,
    NavCampusConnection,
    NavFloorConnection,
    NavLocationConnection,
    NavPlanConnection,
    NavStaticConnection,
    NavTypeConnection,
    resolve_nav_auditories,
    resolve_nav_auditory_photos,
    resolve_nav_campuses,
    resolve_nav_floors,
    resolve_nav_locations,
    resolve_nav_plans,
    resolve_nav_statics,
    resolve_nav_types,
)
from .problem import ProblemType, resolve_problems
from .review import ReviewType, resolve_reviews
from .review_status import ReviewStatusType, resolve_review_status
from .user_id import UserIdType, resolve_user_ids
from .user_role import GoalConnection, resolve_goals
from .user_role import RightConnection, resolve_rights
from .user_role import RoleConnection, RoleType, resolve_role, resolve_roles
from .user_role import (
    RoleRightGoalConnection,
    RoleRightGoalType,
    resolve_role_right_goal,
    resolve_role_right_goals,
)
from .user_role import UserConnection, UserType, resolve_user, resolve_users
from .user_role import (
    UserRoleConnection,
    UserRoleType,
    resolve_user_role,
    resolve_user_roles,
)


@strawberry.type
class Query:
    reviews: list[ReviewType] = strawberry.field(
        resolver=resolve_reviews,
        description="Get user reviews.",
    )
    user_ids: list[UserIdType] = strawberry.field(
        resolver=resolve_user_ids,
        description="Get user ids.",
    )
    problems: list[ProblemType] = strawberry.field(
        resolver=resolve_problems,
        description="Get problems list.",
    )
    review_statuses: list[ReviewStatusType] = strawberry.field(
        resolver=resolve_review_status,
        description="Get review statuses list.",
    )
    endpoint_statistics: list[EndpointStatisticsType] = strawberry.field(
        resolver=resolve_endpoint_statistics,
        description="Get endpoint statistics for selected goal.",
    )
    endpoint_statistics_avg: AggregatedEndpointStatisticsType = strawberry.field(
        resolver=resolve_endpoint_statistics_avg,
        description="Get aggregated endpoint statistics for selected period.",
    )

    nav_floors: NavFloorConnection = strawberry.field(
        resolver=resolve_nav_floors,
        description="Get navigation floors with pagination.",
    )
    nav_locations: NavLocationConnection = strawberry.field(
        resolver=resolve_nav_locations,
        description="Get navigation locations with pagination.",
    )
    nav_campuses: NavCampusConnection = strawberry.field(
        resolver=resolve_nav_campuses,
        description="Get navigation campuses with pagination.",
    )
    nav_plans: NavPlanConnection = strawberry.field(
        resolver=resolve_nav_plans,
        description="Get navigation plans with pagination.",
    )
    nav_statics: NavStaticConnection = strawberry.field(
        resolver=resolve_nav_statics,
        description="Get navigation static resources with pagination.",
    )
    nav_types: NavTypeConnection = strawberry.field(
        resolver=resolve_nav_types,
        description="Get navigation auditory types with pagination.",
    )
    nav_auditories: NavAuditoryConnection = strawberry.field(
        resolver=resolve_nav_auditories,
        description="Get navigation auditories with pagination.",
    )
    nav_auditory_photos: NavAuditoryPhotoConnection = strawberry.field(
        resolver=resolve_nav_auditory_photos,
        description="Get navigation auditory photos with pagination.",
    )

    dod_nav_floors: DodNavFloorConnection = strawberry.field(
        resolver=resolve_dod_nav_floors,
        description="Get DOD navigation floors with pagination.",
    )
    dod_nav_locations: DodNavLocationConnection = strawberry.field(
        resolver=resolve_dod_nav_locations,
        description="Get DOD navigation locations with pagination.",
    )
    dod_nav_campuses: DodNavCampusConnection = strawberry.field(
        resolver=resolve_dod_nav_campuses,
        description="Get DOD navigation campuses with pagination.",
    )
    dod_nav_plans: DodNavPlanConnection = strawberry.field(
        resolver=resolve_dod_nav_plans,
        description="Get DOD navigation plans with pagination.",
    )
    dod_nav_statics: DodNavStaticConnection = strawberry.field(
        resolver=resolve_dod_nav_statics,
        description="Get DOD navigation static resources with pagination.",
    )
    dod_nav_types: DodNavTypeConnection = strawberry.field(
        resolver=resolve_dod_nav_types,
        description="Get DOD navigation auditory types with pagination.",
    )
    dod_nav_auditories: DodNavAuditoryConnection = strawberry.field(
        resolver=resolve_dod_nav_auditories,
        description="Get DOD navigation auditories with pagination.",
    )
    dod_nav_auditory_photos: DodNavAuditoryPhotoConnection = strawberry.field(
        resolver=resolve_dod_nav_auditory_photos,
        description="Get DOD navigation auditory photos with pagination.",
    )

    users: UserConnection = strawberry.field(
        resolver=resolve_users,
        description="Get users with pagination.",
    )
    user: Optional[UserType] = strawberry.field(
        resolver=resolve_user,
        description="Get user.",
    )
    roles: RoleConnection = strawberry.field(
        resolver=resolve_roles,
        description="Get roles with pagination.",
    )
    role: Optional[RoleType] = strawberry.field(
        resolver=resolve_role,
        description="Get role.",
    )
    user_roles: UserRoleConnection = strawberry.field(
        resolver=resolve_user_roles,
        description="Get user_roles with pagination.",
    )
    user_role: Optional[UserRoleType] = strawberry.field(
        resolver=resolve_user_role,
        description="Get user_role.",
    )
    role_right_goals: RoleRightGoalConnection = strawberry.field(
        resolver=resolve_role_right_goals,
        description="Get role_right_goals with pagination.",
    )
    role_right_goal: Optional[RoleRightGoalType] = strawberry.field(
        resolver=resolve_role_right_goal,
        description="Get role_right_goal.",
    )
    rights: RightConnection = strawberry.field(
        resolver=resolve_rights,
        description="Get rights with pagination.",
    )
    goals: GoalConnection = strawberry.field(
        resolver=resolve_goals,
        description="Get goals with pagination.",
    )
