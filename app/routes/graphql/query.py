import strawberry
from .change_plan import ChangePlanType, resolve_change_plans
from .endpoint_stats import EndpointStatisticsType, resolve_endpoint_statistics
from .nav import (
    NavAuditoryType,
    NavCampusType,
    NavFloorType,
    NavLocationType,
    NavPlanType,
    NavStaticType,
    NavTypeType,
    resolve_nav_auditories,
    resolve_nav_campuses,
    resolve_nav_floors,
    resolve_nav_locations,
    resolve_nav_plans,
    resolve_nav_statics,
    resolve_nav_types,
)
from .problem import ProblemType, resolve_problems
from .review import ReviewType, resolve_reviews
from .select_auditory import SelectAuditoryType, resolve_select_auditories
from .site_stat import SiteStatType, resolve_site_stats
from .start_way import StartWayType, resolve_start_ways
from .user_id import UserIdType, resolve_user_ids


@strawberry.type
class Query:
    change_plans: list[ChangePlanType] = strawberry.field(
        resolver=resolve_change_plans,
        description="Получение истории изменений планов."
    )
    reviews: list[ReviewType] = strawberry.field(
        resolver=resolve_reviews,
        description="Получение списка отзывов пользователей."
    )
    start_ways: list[StartWayType] = strawberry.field(
        resolver=resolve_start_ways,
        description="Получение стартовых точек и начальных переходов."
    )
    select_auditories: list[SelectAuditoryType] = strawberry.field(
        resolver=resolve_select_auditories,
        description="Получение списков выбранных аудиторий."
    )
    site_stats: list[SiteStatType] = strawberry.field(
        resolver=resolve_site_stats,
        description="Получение статистики посещений сайта."
    )
    user_ids: list[UserIdType] = strawberry.field(
        resolver=resolve_user_ids,
        description="Получение идентификаторов пользователей и связанных данных."
    )
    problems: list[ProblemType] = strawberry.field(
        resolver=resolve_problems,
        description="Получение списка проблем."
    )
    endpoint_statistics: list[EndpointStatisticsType] = strawberry.field(
        resolver=resolve_endpoint_statistics,
        description="Статистика по эндпоинтам для выбранной цели."
    )
    nav_floors: list[NavFloorType] = strawberry.field(
        resolver=resolve_nav_floors,
        description="Получение этажей навигации."
    )
    nav_locations: list[NavLocationType] = strawberry.field(
        resolver=resolve_nav_locations,
        description="Получение локаций навигации."
    )
    nav_campuses: list[NavCampusType] = strawberry.field(
        resolver=resolve_nav_campuses,
        description="Получение корпусов навигации."
    )
    nav_plans: list[NavPlanType] = strawberry.field(
        resolver=resolve_nav_plans,
        description="Получение планов навигации."
    )
    nav_statics: list[NavStaticType] = strawberry.field(
        resolver=resolve_nav_statics,
        description="Получение статических ресурсов навигации."
    )
    nav_types: list[NavTypeType] = strawberry.field(
        resolver=resolve_nav_types,
        description="Получение типов аудиторий."
    )
    nav_auditories: list[NavAuditoryType] = strawberry.field(
        resolver=resolve_nav_auditories,
        description="Получение аудиторий."
    )
