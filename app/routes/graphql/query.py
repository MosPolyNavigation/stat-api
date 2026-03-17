import strawberry
from .change_plan import ChangePlanType, resolve_change_plans
from .dod import DodNavAuditoryType, DodNavCampusType, DodNavFloorType, DodNavLocationType, DodNavPlanType, DodNavStaticType, DodNavTypeType, resolve_dod_nav_auditories, resolve_dod_nav_campuses, resolve_dod_nav_floors, resolve_dod_nav_locations, resolve_dod_nav_plans, resolve_dod_nav_statics, resolve_dod_nav_types
from .endpoint_stats import AggregatedEndpointStatisticsType, EndpointStatisticsType, resolve_endpoint_statistics, resolve_endpoint_statistics_avg
from .nav import NavAuditoryType, NavCampusType, NavFloorType, NavLocationType, NavPlanType, NavStaticType, NavTypeType, resolve_nav_auditories, resolve_nav_campuses, resolve_nav_floors, resolve_nav_locations, resolve_nav_plans, resolve_nav_statics, resolve_nav_types
from .problem import ProblemType, resolve_problems
from .review import ReviewType, resolve_reviews
from .review_status import ReviewStatusType, resolve_review_status
from .select_auditory import SelectAuditoryType, resolve_select_auditories
from .site_stat import SiteStatType, resolve_site_stats
from .start_way import StartWayType, resolve_start_ways
from .tg_bot import TgBotEventKindType, TgBotEventStatisticType, TgBotEventType, TgBotUserType, resolve_tg_bot_event_statistics, resolve_tg_bot_event_types, resolve_tg_bot_events, resolve_tg_bot_users, AggregatedTgStatisticsType, TgStatisticsType, resolve_tg_bot_event_statistics, resolve_tg_statistics, resolve_tg_statistics_avg
from .user_id import UserIdType, resolve_user_ids
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

    nav_floors: list[NavFloorType] = strawberry.field(
        resolver=resolve_nav_floors,
        description="Get navigation floors.",
    )
    nav_locations: list[NavLocationType] = strawberry.field(
        resolver=resolve_nav_locations,
        description="Get navigation locations.",
    )
    nav_campuses: list[NavCampusType] = strawberry.field(
        resolver=resolve_nav_campuses,
        description="Get navigation campuses.",
    )
    nav_plans: list[NavPlanType] = strawberry.field(
        resolver=resolve_nav_plans,
        description="Get navigation plans.",
    )
    nav_statics: list[NavStaticType] = strawberry.field(
        resolver=resolve_nav_statics,
        description="Get navigation static resources.",
    )
    nav_types: list[NavTypeType] = strawberry.field(
        resolver=resolve_nav_types,
        description="Get navigation auditory types.",
    )
    nav_auditories: list[NavAuditoryType] = strawberry.field(
        resolver=resolve_nav_auditories,
        description="Get navigation auditories.",
    )

    dod_nav_floors: list[DodNavFloorType] = strawberry.field(
        resolver=resolve_dod_nav_floors,
        description="Get DOD navigation floors.",
    )
    dod_nav_locations: list[DodNavLocationType] = strawberry.field(
        resolver=resolve_dod_nav_locations,
        description="Get DOD navigation locations.",
    )
    dod_nav_campuses: list[DodNavCampusType] = strawberry.field(
        resolver=resolve_dod_nav_campuses,
        description="Get DOD navigation campuses.",
    )
    dod_nav_plans: list[DodNavPlanType] = strawberry.field(
        resolver=resolve_dod_nav_plans,
        description="Get DOD navigation plans.",
    )
    dod_nav_statics: list[DodNavStaticType] = strawberry.field(
        resolver=resolve_dod_nav_statics,
        description="Get DOD navigation static resources.",
    )
    dod_nav_types: list[DodNavTypeType] = strawberry.field(
        resolver=resolve_dod_nav_types,
        description="Get DOD navigation auditory types.",
    )
    dod_nav_auditories: list[DodNavAuditoryType] = strawberry.field(
        resolver=resolve_dod_nav_auditories,
        description="Get DOD navigation auditories.",
    )



