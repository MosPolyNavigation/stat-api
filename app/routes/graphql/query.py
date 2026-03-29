import strawberry
from typing import Optional
from .change_plan import ChangePlanType, resolve_change_plans
from .dod import DodNavAuditoryConnection, DodNavAuditoryPhotoConnection, DodNavCampusConnection, DodNavFloorConnection, DodNavLocationConnection, DodNavPlanConnection, DodNavStaticConnection, DodNavTypeConnection, resolve_dod_nav_auditories, resolve_dod_nav_auditory_photos, resolve_dod_nav_campuses, resolve_dod_nav_floors, resolve_dod_nav_locations, resolve_dod_nav_plans, resolve_dod_nav_statics, resolve_dod_nav_types
from .endpoint_stats import AggregatedEndpointStatisticsType, EndpointStatisticsType, resolve_endpoint_statistics, resolve_endpoint_statistics_avg
from .nav import NavAuditoryConnection, NavAuditoryPhotoConnection, NavCampusConnection, NavFloorConnection, NavLocationConnection, NavPlanConnection, NavStaticConnection, NavTypeConnection, resolve_nav_auditories, resolve_nav_auditory_photos, resolve_nav_campuses, resolve_nav_floors, resolve_nav_locations, resolve_nav_plans, resolve_nav_statics, resolve_nav_types
from .problem import ProblemType, resolve_problems
from .review import ReviewType, resolve_reviews
from .review_status import ReviewStatusType, resolve_review_status
from .select_auditory import SelectAuditoryType, resolve_select_auditories
from .site_stat import SiteStatType, resolve_site_stats
from .start_way import StartWayType, resolve_start_ways
from .tg_bot import TgBotEventKindType, TgBotEventStatisticType, TgBotEventType, TgBotUserType, resolve_tg_bot_event_statistics, resolve_tg_bot_event_types, resolve_tg_bot_events, resolve_tg_bot_users, AggregatedTgStatisticsType, TgStatisticsType, resolve_tg_bot_event_statistics, resolve_tg_statistics, resolve_tg_statistics_avg
from .user_id import UserIdType, resolve_user_ids
from .user_role import UserConnection, resolve_users, UserType, resolve_user
from .user_role import RoleConnection, resolve_roles, RoleType, resolve_role
from .user_role import UserRoleConnection, resolve_user_roles, UserRoleType, resolve_user_role
from .user_role import RoleRightGoalConnection, resolve_role_right_goals, RoleRightGoalType, resolve_role_right_goal
from .user_role import RightConnection, resolve_rights
from .user_role import GoalConnection, resolve_goals


@strawberry.type
class Query:
    change_plans: list[ChangePlanType] = strawberry.field(
        resolver=resolve_change_plans,
        description="Get plan changes history.",
    )
    reviews: list[ReviewType] = strawberry.field(
        resolver=resolve_reviews,
        description="Get user reviews.",
    )
    start_ways: list[StartWayType] = strawberry.field(
        resolver=resolve_start_ways,
        description="Get start way statistics.",
    )
    select_auditories: list[SelectAuditoryType] = strawberry.field(
        resolver=resolve_select_auditories,
        description="Get selected auditories statistics.",
    )
    site_stats: list[SiteStatType] = strawberry.field(
        resolver=resolve_site_stats,
        description="Get site visits statistics.",
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
    tg_bot_users: list[TgBotUserType] = strawberry.field(
        resolver=resolve_tg_bot_users,
        description="Get Telegram bot users.",
    )
    tg_bot_event_types: list[TgBotEventKindType] = strawberry.field(
        resolver=resolve_tg_bot_event_types,
        description="Get Telegram bot event kinds.",
    )
    tg_bot_events: list[TgBotEventType] = strawberry.field(
        resolver=resolve_tg_bot_events,
        description="Get Telegram bot events.",
    )
    tg_bot_event_statistics: list[TgBotEventStatisticType] = strawberry.field(
        resolver=resolve_tg_bot_event_statistics,
        description="Get Telegram bot event statistics.",
    )
    tg_stats: list[TgStatisticsType] = strawberry.field(
        name="TgStats",
        resolver=resolve_tg_statistics,
        description="Get Telegram bot statistics grouped by selected period.",
    )
    tg_event_type: list[TgBotEventKindType] = strawberry.field(
        name="TgEventType",
        resolver=resolve_tg_bot_event_types,
        description="Get Telegram bot event types.",
    )
    tg_stats_avg: AggregatedTgStatisticsType = strawberry.field(
        name="TgStatsAvg",
        resolver=resolve_tg_statistics_avg,
        description="Get aggregated Telegram bot statistics for selected period.",
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
        description="Get users with pagination."
    )
    user: Optional[UserType] = strawberry.field(
        resolver=resolve_user,
        description="Get user."
    )
    roles: RoleConnection = strawberry.field(
        resolver=resolve_roles,
        description="Get roles with pagination."
    )
    role: Optional[RoleType] = strawberry.field(
        resolver=resolve_role,
        description="Get role."
    )
    user_roles: UserRoleConnection = strawberry.field(
        resolver=resolve_user_roles,
        description="Get user_roles with pagination."
    )
    user_role: Optional[UserRoleType] = strawberry.field(
        resolver=resolve_user_role,
        description="Get user_role."
    )
    role_right_goals: RoleRightGoalConnection = strawberry.field(
        resolver=resolve_role_right_goals,
        description="Get role_right_goals with pagination."
    )
    role_right_goal: Optional[RoleRightGoalType] = strawberry.field(
        resolver=resolve_role_right_goal,
        description="Get role_right_goal."
    )
    rights: RightConnection = strawberry.field(
        resolver=resolve_rights,
        description="Get rights with pagination."
    )
    goals: GoalConnection = strawberry.field(
        resolver=resolve_goals,
        description="Get goals with pagination."
    )
