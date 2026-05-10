from typing import Optional
from datetime import datetime
import strawberry
from sqlalchemy import select

from app.graphql.core.filters import apply_filters
from app.graphql.core.ordering import apply_order_by
from app.graphql.core.pagination import PaginationInput, paginate_query, Connection
from app.graphql.domains.event_system.inputs import PayloadFilterInput, PayloadOrderByInput
from app.models import (
    EventType as ETModel,
    PayloadType as PTModel,
    ValueType as VTModel,
    ReviewStatus as RSModel,
    ClientId as CIModel,
    Event as EventModel,
    Payload as PayloadModel,
    DashboardType as DTModel,
    Dashboard as DashboardModel,
)
from app.graphql.core.context import GraphQLContext


# =============================================================================
# Helper: конвертеры моделей в типы
# =============================================================================
def _value_type_from_model(model: Optional[VTModel]) -> Optional["ValueType"]:
    if model is None:
        return None
    return ValueType(
        id=model.id,  # type: ignore[call-arg]
        name=model.name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _payload_type_from_model(model: Optional[PTModel]) -> Optional["PayloadType"]:
    if model is None:
        return None
    return PayloadType(
        id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
        value_type_id=model.value_type_id,  # type: ignore[call-arg]
    )


def _event_type_from_model(model: Optional[ETModel]) -> Optional["EventType"]:
    if model is None:
        return None
    return EventType(
        id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _client_id_from_model(model: Optional[CIModel]) -> Optional["ClientId"]:
    if model is None:
        return None
    return ClientId(
        id=model.id,  # type: ignore[call-arg]
        ident=model.ident,  # type: ignore[call-arg]
        creation_date=model.creation_date,  # type: ignore[call-arg]
    )


def _review_status_from_model(model: Optional[RSModel]) -> Optional["ReviewStatus"]:
    if model is None:
        return None
    return ReviewStatus(
        id=model.id,  # type: ignore[call-arg]
        name=model.name,  # type: ignore[call-arg]
    )


def _review_from_model(model) -> Optional["Review"]:
    if model is None:
        return None
    return Review(
        id=model.id,  # type: ignore[call-arg]
        client_id=model.client_id,  # type: ignore[call-arg]
        problem_id=model.problem_id,  # type: ignore[call-arg]
        status_id=model.review_status_id,  # type: ignore[call-arg]
        text=model.text,  # type: ignore[call-arg]
        image_name=model.image_name,  # type: ignore[call-arg]
        creation_date=model.creation_date,  # type: ignore[call-arg]
    )


def _event_from_model(model: EventModel) -> "Event":
    return Event(
        id=model.id,  # type: ignore[call-arg]
        client_id=model.client_id,  # type: ignore[call-arg]
        event_type_id=model.event_type_id,  # type: ignore[call-arg]
        trigger_time=model.trigger_time,  # type: ignore[call-arg]
    )


def _payload_from_model(model: PayloadModel) -> "Payload":
    return Payload(
        id=model.id,  # type: ignore[call-arg]
        event_id=model.event_id,  # type: ignore[call-arg]
        type_id=model.type_id,  # type: ignore[call-arg]
        value=model.value,  # type: ignore[call-arg]
    )


def _dashboard_type_from_model(model: DTModel) -> "DashboardType":
    return DashboardType(
        id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _dashboard_from_model(model: DashboardModel) -> "Dashboard":
    return Dashboard(  # type: ignore
        id=model.id,
        display_order=model.display_order,
        event_type_id=model.event_type_id,
        dashboard_type_id=model.dashboard_type_id,
        title_text=model.title_text,
    )


# =============================================================================
# Strawberry Types
# =============================================================================

@strawberry.type
class ValueType:
    """Тип значения (int/string/bool)."""
    id: int
    name: str
    description: Optional[str] = None


@strawberry.type
class PayloadType:
    """Тип полезной нагрузки события."""
    id: int
    code_name: str
    description: Optional[str] = None
    value_type_id: int

    @strawberry.field  # type: ignore[unresolved-reference]
    async def value_type(self, info: strawberry.Info) -> Optional["ValueType"]:
        """Ленивая загрузка связанного ValueType через DataLoader."""
        ctx: GraphQLContext = info.context
        vt_model = await ctx.loaders["value_type"].load(self.value_type_id)
        return _value_type_from_model(vt_model) if vt_model else None


@strawberry.type
class EventType:
    """Тип события (site/auds/ways/plans)."""
    id: int
    code_name: str
    description: Optional[str] = None


@strawberry.type
class AllowedPayloadRule:
    """
    Правило: какой PayloadType допустим для какого EventType.
    Использует составной первичный ключ (event_type_id, payload_type_id).
    """
    event_type_id: int
    payload_type_id: int

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event_type(self, info: strawberry.Info) -> Optional[EventType]:
        ctx: GraphQLContext = info.context
        et_model = await ctx.loaders["event_type"].load(self.event_type_id)
        return _event_type_from_model(et_model) if et_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def payload_type(self, info: strawberry.Info) -> Optional[PayloadType]:
        ctx: GraphQLContext = info.context
        pt_model = await ctx.loaders["payload_type"].load(self.payload_type_id)
        return _payload_type_from_model(pt_model) if pt_model else None


@strawberry.type
class ClientId:
    """Идентификатор клиента."""
    id: int
    ident: str
    creation_date: datetime


@strawberry.type
class Problem:
    """Тип проблемы (string ID)."""
    id: str


@strawberry.type
class ReviewStatus:
    """Статус отзыва."""
    id: int
    name: str


@strawberry.type
class Review:
    """Отзыв пользователя."""
    id: int
    client_id: int
    problem_id: str
    status_id: int
    text: str
    image_name: Optional[str]
    creation_date: datetime

    @strawberry.field  # type: ignore[unresolved-reference]
    async def client(self, info: strawberry.Info) -> Optional[ClientId]:
        ctx: GraphQLContext = info.context
        ci_model = await ctx.loaders["client_id"].load(self.client_id)
        return _client_id_from_model(ci_model) if ci_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def problem(self, _info: strawberry.Info) -> Optional[Problem]:
        return Problem(id=self.problem_id) if self.problem_id else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def status(self, info: strawberry.Info) -> Optional[ReviewStatus]:
        ctx: GraphQLContext = info.context
        rs_model = await ctx.loaders["review_status"].load(self.status_id)
        return _review_status_from_model(rs_model) if rs_model else None


@strawberry.type
class Event:
    """Событие, сгенерированное клиентом."""
    id: int
    client_id: int
    event_type_id: int
    trigger_time: datetime

    @strawberry.field  # type: ignore[unresolved-reference]
    async def client(self, info: strawberry.Info) -> Optional[ClientId]:
        ctx: GraphQLContext = info.context
        ci_model = await ctx.loaders["client_id"].load(self.client_id)
        return _client_id_from_model(ci_model) if ci_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event_type(self, info: strawberry.Info) -> Optional[EventType]:
        ctx: GraphQLContext = info.context
        et_model = await ctx.loaders["event_type"].load(self.event_type_id)
        return _event_type_from_model(et_model) if et_model else None

    @strawberry.field()
    async def payloads(
        self,
        info: strawberry.Info,  # noqa
        pagination: Optional[PaginationInput] = None,
        filter: Optional[PayloadFilterInput] = None,
        order_by: Optional[PayloadOrderByInput] = None,
    ) -> Connection["Payload"]:
        """Построение запроса для пейлоадов текущего события."""
        ctx: GraphQLContext = info.context
        stmt = select(PayloadModel).where(PayloadModel.event_id == self.id)
        if filter:
            stmt = apply_filters(stmt, PayloadModel, filter)
        if order_by:
            stmt = apply_order_by(stmt, PayloadModel, order_by)
        if pagination is None:
            pagination = PaginationInput(page=1, page_size=10)  # noqa
        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_payload_from_model,
        )


@strawberry.type
class Payload:
    """Полезная нагрузка события."""
    id: int
    event_id: int
    type_id: int
    value: str

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event(self, info: strawberry.Info) -> Optional[Event]:
        ctx: GraphQLContext = info.context
        ev_model = await ctx.db.get(EventModel, self.event_id)
        return _event_from_model(ev_model) if ev_model else None  # noqa

    @strawberry.field  # type: ignore[unresolved-reference]
    async def payload_type(self, info: strawberry.Info) -> Optional[PayloadType]:
        ctx: GraphQLContext = info.context
        pt_model = await ctx.loaders["payload_type"].load(self.type_id)
        return _payload_type_from_model(pt_model) if pt_model else None


@strawberry.type
class DashboardType:
    """Справочник типов дашбордов."""
    id: int
    code_name: str
    description: Optional[str] = None


@strawberry.type
class Dashboard:
    """Дашборд для отображения статистики."""
    id: int
    display_order: int
    event_type_id: int
    dashboard_type_id: int
    title_text: str

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event_type(self, info: strawberry.Info) -> Optional[EventType]:
        ctx: GraphQLContext = info.context
        et_model = await ctx.loaders["event_type"].load(self.event_type_id)
        return _event_type_from_model(et_model) if et_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def dashboard_type(self, info: strawberry.Info) -> Optional[DashboardType]:
        ctx: GraphQLContext = info.context
        dt_model = await ctx.loaders["dashboard_type"].load(self.dashboard_type_id)
        return _dashboard_type_from_model(dt_model) if dt_model else None
