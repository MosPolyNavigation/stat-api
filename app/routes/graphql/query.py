"""GraphQL Query тип со всеми доступными выборками."""

import strawberry

from .change_plan import ChangePlanType, resolve_change_plans
from .endpoint_stats import EndpointStatisticsType, resolve_endpoint_statistics
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
        description="История переключений планов пользователями.",
    )
    reviews: list[ReviewType] = strawberry.field(
        resolver=resolve_reviews,
        description="Отзывы пользователей.",
    )
    start_ways: list[StartWayType] = strawberry.field(
        resolver=resolve_start_ways,
        description="Попытки построения маршрутов.",
    )
    select_auditories: list[SelectAuditoryType] = strawberry.field(
        resolver=resolve_select_auditories,
        description="Выбор аудиторий пользователями.",
    )
    site_stats: list[SiteStatType] = strawberry.field(
        resolver=resolve_site_stats,
        description="Статистика посещения сайта.",
    )
    user_ids: list[UserIdType] = strawberry.field(
        resolver=resolve_user_ids,
        description="Список зарегистрированных user_id.",
    )
    problems: list[ProblemType] = strawberry.field(
        resolver=resolve_problems,
        description="Справочник типов проблем.",
    )
    endpoint_statistics: list[EndpointStatisticsType] = strawberry.field(
        resolver=resolve_endpoint_statistics,
        description="Статистика по REST-эндпоинтам для выбранной цели.",
    )
