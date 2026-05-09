from typing import Optional, Iterable

import strawberry
from strawberry import relay, Info
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    EventType, PayloadType, ValueType,
    AllowedPayload, Review as ReviewModel, ClientId as CIModel
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
)
from .inputs import (
    EventTypeFilterInput,
    PayloadTypeFilterInput,
    ValueTypeFilterInput,
    AllowedPayloadRuleFilterInput,
    ReviewFilterInput,
    ClientIdFilterInput,
)


# =============================================================================
# Локальные конвертеры (для передачи в fetch_relay_page)
# =============================================================================
def _event_type_from_model(model: EventType) -> EventTypeType:
    return EventTypeType(
        db_id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _payload_type_from_model(model: PayloadType) -> PayloadTypeType:
    return PayloadTypeType(
        db_id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
        value_type_id=model.value_type_id,  # type: ignore[call-arg]
    )


def _value_type_from_model(model: ValueType) -> ValueTypeType:
    return ValueTypeType(
        db_id=model.id,  # type: ignore[call-arg]
        name=model.name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _client_id_from_model(model: CIModel) -> ClientIdType:
    return ClientIdType(
        db_id=model.id,  # type: ignore[call-arg]
        ident=model.ident,  # type: ignore[call-arg]
        creation_date=model.creation_date,  # type: ignore[call-arg]
    )


def _review_from_model(model: ReviewModel) -> ReviewType:
    return ReviewType(
        db_id=model.id,  # type: ignore[call-arg]
        client_id=model.client_id,  # type: ignore[call-arg]
        problem_id=model.problem_id,  # type: ignore[call-arg]
        status_id=model.review_status_id,  # type: ignore[call-arg]
        text=model.text,  # type: ignore[call-arg]
        image_name=model.image_name,  # type: ignore[call-arg]
        creation_date=model.creation_date,  # type: ignore[call-arg]
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
            convert=_event_type_from_model,
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
            convert=_payload_type_from_model,
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
            convert=_value_type_from_model,
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
            convert=_client_id_from_model,
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
            cursor_fields="id",  # ← id как tiebreaker для стабильности
            convert=_review_from_model,
        )

    @strawberry.field  # type: ignore[unresolved-reference]
    async def review(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> Optional[ReviewType]:
        """Получение одного отзыва по глобальному ID."""
        await require_permissions(info, P.REVIEWS_VIEW)
        return await id.resolve_node(info, ensure_type=ReviewType)
