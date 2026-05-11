from typing import Optional
import strawberry
from strawberry import Info
from sqlalchemy import select

from app.graphql.core.ordering import apply_order_by
from app.graphql.core.pagination import paginate_query, PaginationInput, Connection
from app.graphql.core.resource_factory import create_query_resource
from app.graphql.domains.event_system.resources import (
    EventTypeResource,
    PayloadTypeResource,
    ValueTypeResource,
    ClientIdResource,
    ReviewResource,
    EventResource,
    PayloadResource,
    DashboardResource,
    DashboardTypeResource,
    ReviewStatusResource
)
from app.models import AllowedPayload
from app.graphql.core.permissions import require_permissions, P
from app.graphql.core.filters import apply_filters
from app.graphql.core.context import GraphQLContext
from app.graphql.domains.event_system.types import (
    AllowedPayloadRule as AllowedPayloadRuleType,
)
from app.graphql.domains.event_system.inputs import (
    AllowedPayloadRuleFilterInput,
    AllowedPayloadRuleOrderByInput
)

# =============================================================================
# Генерация ресурсов через фабрику
# =============================================================================

EventTypeQuery = create_query_resource(
    EventTypeResource,
    name_list="event_types",
    name_get="event_type",
)

PayloadTypeQuery = create_query_resource(
    PayloadTypeResource,
    name_list="payload_types",
    name_get="payload_type",
)

ValueTypeQuery = create_query_resource(
    ValueTypeResource,
    name_list="value_types",
    name_get="value_type",
)

ClientIdQuery = create_query_resource(
    ClientIdResource,
    name_list="client_ids",
    name_get="client_id",
)

ReviewQuery = create_query_resource(
    ReviewResource,
    name_get="review",
    name_list="reviews",
)

EventQuery = create_query_resource(
    EventResource,
    name_list="events",
    name_get="event",
)

PayloadQuery = create_query_resource(
    PayloadResource,
    name_list="payloads",
    name_get="payload",
)

DashboardQuery = create_query_resource(
    DashboardResource,
    name_list="dashboards",
    name_get="dashboard",
)

DashboardTypeQuery = create_query_resource(
    DashboardTypeResource,
    name_list="dashboard_types",
    name_get="dashboard_type",
)

ReviewStatusQuery = create_query_resource(
    ReviewStatusResource,
    name_list="review_statuses",
    name_get="review_status",
)


# =============================================================================
# Ручная реализация для AllowedPayloadRule (составной ключ)
# =============================================================================
@strawberry.type
class AllowedPayloadRuleQuery:
    # 🔹 Используем наш кастомный декоратор пагинации
    @strawberry.field  # type: ignore[unresolved-reference]
    async def allowed_payload_rules(
            self,
            info: Info,
            pagination: Optional[PaginationInput] = None,
            filter: Optional[AllowedPayloadRuleFilterInput] = None,
            order_by: Optional[AllowedPayloadRuleOrderByInput] = None,
    ) -> Connection[AllowedPayloadRuleType]:
        """Построение запроса для правил — декоратор применит пагинацию."""
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(AllowedPayload)
        if filter:
            stmt = apply_filters(stmt, AllowedPayload, filter)
        if order_by:
            stmt = apply_order_by(stmt, AllowedPayload, order_by)

        if pagination is None:
            pagination = PaginationInput(page=1, page_size=10)  # noqa

        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=lambda m: AllowedPayloadRuleType(
                event_type_id=m.event_type_id,  # type: ignore[call-arg]
                payload_type_id=m.payload_type_id,  # type: ignore[call-arg]
            ),
        )

    # 🔹 Одиночный запрос с составным ключом (два int аргумента)
    @strawberry.field  # type: ignore[unresolved-reference]
    async def allowed_payload_rule(
            self,
            info: Info,
            event_type_id: int,
            payload_type_id: int,
    ) -> Optional[AllowedPayloadRuleType]:
        """Получение правила по составному ключу."""
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(AllowedPayload).where(
            AllowedPayload.event_type_id == event_type_id,
            AllowedPayload.payload_type_id == payload_type_id,
        )
        model = (await ctx.db.execute(stmt)).scalar_one_or_none()

        if model:
            return AllowedPayloadRuleType(
                event_type_id=model.event_type_id,  # type: ignore[call-arg]
                payload_type_id=model.payload_type_id,  # type: ignore[call-arg]
            )
        return None


# =============================================================================
# Корневой Query: объединяем всё
# =============================================================================
@strawberry.type
class Query(
    EventTypeQuery,
    PayloadTypeQuery,
    ValueTypeQuery,
    ClientIdQuery,
    ReviewQuery,
    EventQuery,
    PayloadQuery,
    DashboardQuery,
    DashboardTypeQuery,
    ReviewStatusQuery,
    AllowedPayloadRuleQuery,
):
    """
    Корневой Query для домена event_system.

    Авто-генерированные методы:
    - event_types / event_type
    - payload_types / payload_type
    - value_types / value_type
    - client_ids / client_id
    - reviews / review
    - events / event
    - payloads / payload
    - dashboards / dashboard
    - dashboard_types / dashboard_type
    - review_statuses / review_status

    Ручная реализация:
    - allowed_payload_rules / allowed_payload_rule (составной ключ)
    """
    pass
