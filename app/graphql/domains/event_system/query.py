from typing import Optional, Iterable

import strawberry
from strawberry import relay, Info
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    EventType, PayloadType, ValueType,
    AllowedPayload, Review as ReviewModel, ClientId as CIModel,
    Event as EventModel, Payload as PayloadModel
)
from app.graphql.core.permissions import require_permissions, P
from app.graphql.core.filters import apply_filters
from app.graphql.core.pagination import fetch_relay_page
from app.graphql.core.context import GraphQLContext

from .types import (
    EventType as EventTypeType,
    PayloadType as PayloadTypeType,
    ValueType as ValueTypeType,
    AllowedPayloadRule as AllowedPayloadRuleType,
    ReviewType,
    ClientIdType,
    Event,
    Payload,
)
from .types import (
    _event_type_from_model,
    _value_type_from_model,
    _payload_type_from_model,
    _client_id_from_model,
    _review_from_model,
    _event_from_model,
    _payload_from_model,
)
from .inputs import (
    EventTypeFilterInput,
    PayloadTypeFilterInput,
    ValueTypeFilterInput,
    AllowedPayloadRuleFilterInput,
    ReviewFilterInput,
    ClientIdFilterInput,
    EventFilterInput,
    PayloadFilterInput,
)


@strawberry.type
class Query:
    # -------------------------------------------------------------------------
    # EventType
    # -------------------------------------------------------------------------
    @relay.connection(relay.ListConnection[EventTypeType])
    async def event_types(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[EventTypeFilterInput] = None,
    ) -> Iterable[EventTypeType]:
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(EventType).order_by(EventType.id.asc())
        if filter:
            stmt = apply_filters(stmt, EventType, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=EventType,
            cursor_fields="id",
            convert=_event_type_from_model,  # type: ignore
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event_type(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[EventTypeType]:
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=EventTypeType)

    # -------------------------------------------------------------------------
    # PayloadType
    # -------------------------------------------------------------------------
    @relay.connection(relay.ListConnection[PayloadTypeType])
    async def payload_types(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[PayloadTypeFilterInput] = None,
    ) -> Iterable[PayloadTypeType]:
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(PayloadType).order_by(PayloadType.id.asc())
        if filter:
            stmt = apply_filters(stmt, PayloadType, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=PayloadType,
            cursor_fields="id",
            convert=_payload_type_from_model,  # type: ignore
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def payload_type(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[PayloadTypeType]:
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=PayloadTypeType)

    # -------------------------------------------------------------------------
    # ValueType
    # -------------------------------------------------------------------------
    @relay.connection(relay.ListConnection[ValueTypeType])
    async def value_types(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[ValueTypeFilterInput] = None,
    ) -> Iterable[ValueTypeType]:
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(ValueType).order_by(ValueType.id.asc())
        if filter:
            stmt = apply_filters(stmt, ValueType, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=ValueType,
            cursor_fields="id",
            convert=_value_type_from_model,  # type: ignore
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def value_type(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[ValueTypeType]:
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=ValueTypeType)

    # -------------------------------------------------------------------------
    # AllowedPayloadRule (составной ключ)
    # -------------------------------------------------------------------------
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

        # ⚠️ ORDER BY должен совпадать с порядком cursor_fields!
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
            cursor_fields=["event_type_id", "payload_type_id"],  # ← составной ключ
            cursor_separator=":",  # курсор вида "1:2"
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
        """Получение одного правила по глобальному ID."""
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=AllowedPayloadRuleType)

    # -------------------------------------------------------------------------
    # ClientId
    # -------------------------------------------------------------------------
    @relay.connection(relay.ListConnection[ClientIdType])
    async def client_ids(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[ClientIdFilterInput] = None,
    ) -> Iterable[ClientIdType]:
        """Список идентификаторов клиентов с пагинацией и фильтрацией."""
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        # Курсорим по id (стабильный int), но сортируем по дате + id для удобства
        stmt = select(CIModel).order_by(
            CIModel.creation_date.desc(),
            CIModel.id.asc()
        )
        if filter:
            stmt = apply_filters(stmt, CIModel, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=CIModel,
            cursor_fields="id",  # ← курсор по стабильному полю
            convert=_client_id_from_model,  # type: ignore
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def client_id(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[ClientIdType]:
        """Получение одного клиента по глобальному ID."""
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=ClientIdType)

    # -------------------------------------------------------------------------
    # Review
    # -------------------------------------------------------------------------
    @relay.connection(relay.ListConnection[ReviewType])
    async def reviews(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[ReviewFilterInput] = None,
    ) -> Iterable[ReviewType]:
        await require_permissions(info, P.REVIEWS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = (
            select(ReviewModel)
            .options(
                selectinload(ReviewModel.client),
                selectinload(ReviewModel.review_status),
            )
            .order_by(ReviewModel.creation_date.desc(), ReviewModel.id.asc())
        )
        if filter:
            stmt = apply_filters(stmt, ReviewModel, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=ReviewModel,
            cursor_fields="id",
            convert=_review_from_model,
        )  # type: ignore[return-value]

    @strawberry.field  # type: ignore[unresolved-reference]
    async def review(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[ReviewType]:
        """Получение одного отзыва по глобальному ID."""
        await require_permissions(info, P.REVIEWS_VIEW)
        return await id.resolve_node(info, ensure_type=ReviewType)

    # -------------------------------------------------------------------------
    # Event
    # -------------------------------------------------------------------------
    @relay.connection(relay.ListConnection[Event])
    async def events(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[EventFilterInput] = None,
    ) -> Iterable[Event]:
        await require_permissions(info, P.STATS_VIEW)  # или P.EVENTS_VIEW
        ctx: GraphQLContext = info.context

        stmt = select(EventModel).order_by(EventModel.id.asc())
        if filter:
            stmt = apply_filters(stmt, EventModel, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=EventModel,
            cursor_fields="id",
            convert=_event_from_model,
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[Event]:
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=Event)

    # -------------------------------------------------------------------------
    # Payload
    # -------------------------------------------------------------------------
    @relay.connection(relay.ListConnection[Payload])
    async def payloads(
            self,
            info: Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
            filter: Optional[PayloadFilterInput] = None,
    ) -> Iterable[Payload]:
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context

        stmt = select(PayloadModel).order_by(PayloadModel.id.asc())
        if filter:
            stmt = apply_filters(stmt, PayloadModel, filter)

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=PayloadModel,
            cursor_fields="id",
            convert=_payload_from_model,
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def payload(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[Payload]:
        await require_permissions(info, P.STATS_VIEW)
        return await id.resolve_node(info, ensure_type=Payload)
