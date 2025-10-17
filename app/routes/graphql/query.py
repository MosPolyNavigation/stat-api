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
        description="Получить список изменений планов."
    )
    reviews: list[ReviewType] = strawberry.field(
        resolver=resolve_reviews,
        description="Получить отзывы пользователей."
    )
    start_ways: list[StartWayType] = strawberry.field(
        resolver=resolve_start_ways,
        description="Получить данные о построенных маршрутах."
    )
    select_auditories: list[SelectAuditoryType] = strawberry.field(
        resolver=resolve_select_auditories,
        description="Получить статистику выбора аудиторий."
    )
    site_stats: list[SiteStatType] = strawberry.field(
        resolver=resolve_site_stats,
        description="Получить статистику посещения эндпоинтов."
    )
    user_ids: list[UserIdType] = strawberry.field(
        resolver=resolve_user_ids,
        description="Получить зарегистрированные идентификаторы пользователей."
    )
    problems: list[ProblemType] = strawberry.field(
        resolver=resolve_problems,
        description="Получить список проблем."
    )
    endpoint_statistics: list[EndpointStatisticsType] = strawberry.field(
        resolver=resolve_endpoint_statistics,
        description="Endpoint statistics for the requested target."
    )
