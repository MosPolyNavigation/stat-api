from typing import Optional, Iterable
import strawberry
from strawberry import relay, Info
from sqlalchemy import select

from app.graphql.core.resource_factory import create_query_resource
from app.graphql.domains.event_system.resources import (
    EventTypeResource,
    PayloadTypeResource,
    ValueTypeResource,
    ClientIdResource,
    ReviewResource,
    EventResource,
    PayloadResource,
)
from app.models import AllowedPayload
from app.graphql.core.permissions import require_permissions, P
from app.graphql.core.filters import apply_filters
from app.graphql.core.pagination import fetch_relay_page
from app.graphql.core.context import GraphQLContext
from app.graphql.domains.event_system.types import AllowedPayloadRule as AllowedPayloadRuleType
from app.graphql.domains.event_system.inputs import AllowedPayloadRuleFilterInput

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


# =============================================================================
# Ручная реализация для AllowedPayloadRule (составной ключ)
# =============================================================================
@strawberry.type
class AllowedPayloadRuleQuery:
    @relay.connection(relay.ListConnection[AllowedPayloadRuleType])
    async def allowed_payload_rules(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[AllowedPayloadRuleFilterInput] = None,
    ) -> Iterable[AllowedPayloadRuleType]:
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(AllowedPayload).order_by(
            AllowedPayload.event_type_id.asc(),
            AllowedPayload.payload_type_id.asc()
        )
        if filter:
            stmt = apply_filters(stmt, AllowedPayload, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=AllowedPayload,
            cursor_fields=["event_type_id", "payload_type_id"],
            cursor_separator=":",
            convert=lambda m: AllowedPayloadRuleType(
                event_type_id=m.event_type_id,  # type: ignore[call-arg]
                payload_type_id=m.payload_type_id,  # type: ignore[call-arg]
                _composite_key=f"{m.event_type_id}:{m.payload_type_id}"  # type: ignore[call-arg]
            ),
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def allowed_payload_rule(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[AllowedPayloadRuleType]:
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=AllowedPayloadRuleType)


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
    AllowedPayloadRuleQuery,  # ← Ручная реализация
):
    """
    Корневой Query для домена event_system.

    Авто-генерированные методы:
    - event_types / event_type
    - payload_types / payload_type
    - value_types / value_type
    - client_ids / client_id
    - reviews (только список)
    - events / event
    - payloads / payload

    Ручная реализация:
    - allowed_payload_rules / allowed_payload_rule (составной ключ)
    """
    pass
