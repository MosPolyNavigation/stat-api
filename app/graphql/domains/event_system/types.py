from typing import Optional, Iterable

from datetime import datetime

import strawberry
from strawberry import relay
from sqlalchemy import select

from app.models import (
    EventType as ETModel,
    PayloadType as PTModel,
    ValueType as VTModel,
    AllowedPayload as APModel,
    ReviewStatus as RSModel,
    ClientId as CIModel,
    Event as EventModel,
    Payload as PayloadModel,
    DashboardType as DTModel,
    Dashboard as DashboardModel,
)
from app.graphql.core.context import GraphQLContext


# =============================================================================
# Helper: конвертеры моделей в типы (для повторного использования)
# =============================================================================
def _value_type_from_model(model: Optional[VTModel]) -> Optional["ValueType"]:
    """Конвертирует модель SQLAlchemy в GraphQL-тип ValueType."""
    if model is None:
        return None
    return ValueType(
        db_id=model.id,  # type: ignore[call-arg]
        name=model.name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _payload_type_from_model(model: Optional[PTModel]) -> Optional["PayloadType"]:
    """Конвертирует модель PayloadType в GraphQL-тип."""
    if model is None:
        return None
    return PayloadType(
        db_id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
        value_type_id=model.value_type_id,  # type: ignore[call-arg]
    )


def _event_type_from_model(model: Optional[ETModel]) -> Optional["EventType"]:
    """Конвертирует модель EventType в GraphQL-тип."""
    if model is None:
        return None
    return EventType(
        db_id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _client_id_from_model(model: Optional[CIModel]) -> Optional["ClientId"]:
    """Конвертирует модель ClientId в GraphQL-тип ClientIdType."""
    if model is None:
        return None
    return ClientId(
        db_id=model.id,  # type: ignore[call-arg]
        ident=model.ident,  # type: ignore[call-arg]
        creation_date=model.creation_date,  # type: ignore[call-arg]
    )


def _review_status_from_model(model: Optional[RSModel]) -> Optional["ReviewStatus"]:
    """Конвертирует модель ReviewStatus в GraphQL-тип."""
    if model is None:
        return None
    return ReviewStatus(
        db_id=model.id,  # type: ignore[call-arg]
        name=model.name,  # type: ignore[call-arg]
    )


def _review_from_model(model) -> Optional["Review"]:
    """Конвертирует модель Review в GraphQL-тип."""
    if model is None:
        return None
    return Review(
        db_id=model.id,  # type: ignore[call-arg]
        client_id=model.client_id,  # type: ignore[call-arg]
        problem_id=model.problem_id,  # type: ignore[call-arg]
        status_id=model.review_status_id,  # type: ignore[call-arg]
        text=model.text,  # type: ignore[call-arg]
        image_name=model.image_name,  # type: ignore[call-arg]
        creation_date=model.creation_date,  # type: ignore[call-arg]
    )


def _event_from_model(model: EventModel) -> "Event":
    return Event(
        db_id=model.id,  # type: ignore[call-arg]
        client_id=model.client_id,  # type: ignore[call-arg]
        event_type_id=model.event_type_id,  # type: ignore[call-arg]
        trigger_time=model.trigger_time,  # type: ignore[call-arg]
    )


def _payload_from_model(model: PayloadModel) -> "Payload":
    return Payload(
        db_id=model.id,  # type: ignore[call-arg]
        event_id=model.event_id,  # type: ignore[call-arg]
        type_id=model.type_id,  # type: ignore[call-arg]
        value=model.value,  # type: ignore[call-arg]
    )


def _dashboard_type_from_model(model: DTModel) -> "DashboardType":
    return DashboardType(
        db_id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _dashboard_from_model(model: DashboardModel) -> "Dashboard":
    return Dashboard(  # type: ignore
        db_id=model.id,
        display_order=model.display_order,
        event_type_id=model.event_type_id,
        dashboard_type_id=model.dashboard_type_id,
        title_text=model.title_text,
    )


# =============================================================================
# Relay Node Types
# =============================================================================

@strawberry.type
class ValueType(relay.Node):
    """Тип значения (int/string/bool)."""
    db_id: relay.NodeID[int]  # noqa
    name: str
    description: Optional[str] = None

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки ValueType по глобальным ID."""
        ctx: GraphQLContext = info.context
        raw_ids = node_ids

        stmt = select(VTModel).where(VTModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        # ✅ Конвертируем модели в типы
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_value_type_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"ValueType {rid} not found")

        return [n for n in nodes if n is not None]


@strawberry.type
class PayloadType(relay.Node):
    """Тип полезной нагрузки события."""
    db_id: relay.NodeID[int]  # noqa
    code_name: str
    description: Optional[str] = None
    value_type_id: int

    @strawberry.field  # type: ignore[unresolved-reference]
    async def value_type(self, info: strawberry.Info) -> Optional["ValueType"]:
        """Ленивая загрузка связанного ValueType через DataLoader (N+1 safe)."""
        ctx: GraphQLContext = info.context

        pt = await ctx.db.get(PTModel, self.db_id)
        if pt and pt.value_type_id:
            vt_model = await ctx.loaders["value_type"].load(pt.value_type_id)
            return _value_type_from_model(vt_model)  # type: ignore[return-value]
        return None

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки PayloadType по глобальным ID."""
        ctx: GraphQLContext = info.context
        raw_ids = node_ids

        stmt = select(PTModel).where(PTModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        # ✅ Конвертируем модели в типы
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_payload_type_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"PayloadType {rid} not found")

        return [n for n in nodes if n is not None]


@strawberry.type
class EventType(relay.Node):
    """Тип события (site/auds/ways/plans)."""
    db_id: relay.NodeID[int]  # noqa
    code_name: str
    description: Optional[str] = None

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки EventType по глобальным ID."""
        ctx: GraphQLContext = info.context
        raw_ids = node_ids

        stmt = select(ETModel).where(ETModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        # ✅ Конвертируем модели в типы
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_event_type_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"EventType {rid} not found")

        return [n for n in nodes if n is not None]


@strawberry.type
class AllowedPayloadRule(relay.Node):
    """
    Правило: какой PayloadType допустим для какого EventType.
    Использует составной первичный ключ (event_type_id, payload_type_id).
    """
    event_type_id: int
    payload_type_id: int

    _composite_key: relay.NodeID[str]  # noqa

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event_type(self, info: strawberry.Info) -> Optional[EventType]:
        ctx: GraphQLContext = info.context
        et_model = await ctx.loaders["event_type"].load(self.event_type_id)
        if et_model:
            return EventType(
                db_id=et_model.id,  # type: ignore[call-arg]
                code_name=et_model.code_name,  # type: ignore[call-arg]
                description=et_model.description,  # type: ignore[call-arg]
            )
        return None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def payload_type(self, info: strawberry.Info) -> Optional[PayloadType]:
        ctx: GraphQLContext = info.context
        pt_model = await ctx.loaders["payload_type"].load(self.payload_type_id)
        if pt_model:
            return PayloadType(
                db_id=pt_model.id,  # type: ignore[call-arg]
                code_name=pt_model.code_name,  # type: ignore[call-arg]
                description=pt_model.description,  # type: ignore[call-arg]
                value_type_id=pt_model.value_type_id,  # type: ignore[call-arg]
            )
        return None

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """
        Загрузка правил по составным ключам.

        Важно: node_ids здесь — это сырые значения _composite_key (например, "1:2"),
        а не полные GlobalID. Strawberry автоматически декодирует GlobalID перед вызовом.
        """
        ctx: GraphQLContext = info.context
        rules = []

        for composite_key in node_ids:  # ← Уже декодировано: "event_id:payload_id"
            event_id, payload_id = map(int, composite_key.split(":"))

            stmt = select(APModel).where(
                APModel.event_type_id == event_id,
                APModel.payload_type_id == payload_id
            )
            item = (await ctx.db.execute(stmt)).scalar_one_or_none()

            if item:
                # ← При создании экземпляра обязательно задаём _composite_key
                rules.append(AllowedPayloadRule(
                    event_type_id=item.event_type_id,  # type: ignore[call-arg]
                    payload_type_id=item.payload_type_id,  # type: ignore[call-arg]
                    _composite_key=f"{item.event_type_id}:{item.payload_type_id}"  # type: ignore[call-arg]
                ))
            elif required:
                raise ValueError(f"Rule {composite_key} not found")

        return rules


# =============================================================================
# Простые типы → Relay Nodes
# =============================================================================

@strawberry.type
class ClientId(relay.Node):
    """Идентификатор клиента."""
    db_id: relay.NodeID[int]  # noqa
    ident: str
    creation_date: datetime

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки клиентов по глобальным ID."""
        ctx: GraphQLContext = info.context
        raw_ids = node_ids

        stmt = select(CIModel).where(CIModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        # ✅ Конвертируем модели в типы
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_client_id_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"ClientId {rid} not found")

        return [n for n in nodes if n is not None]


@strawberry.type
class Problem:
    """Тип проблемы (string ID)."""
    id: str


@strawberry.type
class ReviewStatus(relay.Node):
    """Статус отзыва."""
    db_id: relay.NodeID[int]  # noqa
    name: str

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки статусов по глобальным ID."""
        ctx: GraphQLContext = info.context
        raw_ids = node_ids

        stmt = select(RSModel).where(RSModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        # ✅ Конвертируем модели в типы
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_review_status_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"ReviewStatus {rid} not found")

        return [n for n in nodes if n is not None]


@strawberry.type
class Review(relay.Node):
    """Отзыв пользователя."""
    db_id: relay.NodeID[int]  # noqa
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
        if ci_model:
            # ← Используем db_id, а не id, при создании Relay-типа
            return _client_id_from_model(ci_model)
        return None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def problem(self, _info: strawberry.Info) -> Optional[Problem]:
        return Problem(id=self.problem_id) if self.problem_id else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def status(self, info: strawberry.Info) -> Optional[ReviewStatus]:
        ctx: GraphQLContext = info.context
        rs_model = await ctx.loaders["review_status"].load(self.status_id)
        if rs_model:
            return _review_status_from_model(rs_model)
        return None

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки Review по глобальным ID."""
        from app.models import Review as ReviewModel

        ctx: GraphQLContext = info.context
        raw_ids = node_ids

        stmt = select(ReviewModel).where(ReviewModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        # ✅ Конвертируем модели в типы
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_review_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"Review {rid} not found")

        return [n for n in nodes if n is not None]


# =============================================================================
# Event & Payload Relay Nodes
# =============================================================================
@strawberry.type
class Event(relay.Node):
    """Событие, сгенерированное клиентом."""
    db_id: relay.NodeID[int]  # noqa
    client_id: int
    event_type_id: int
    trigger_time: datetime

    @strawberry.field  # type: ignore[unresolved-reference]
    async def client(self, info: strawberry.Info) -> Optional[ClientId]:
        ctx: GraphQLContext = info.context
        ci_model = await ctx.loaders["client_id"].load(self.client_id)
        return _client_id_from_model(ci_model) if ci_model else None  # type: ignore[call-arg]

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event_type(self, info: strawberry.Info) -> Optional[EventType]:
        ctx: GraphQLContext = info.context
        et_model = await ctx.loaders["event_type"].load(self.event_type_id)
        return EventType(
            db_id=et_model.id,
            code_name=et_model.code_name,
            description=et_model.description
        ) if et_model else None  # type: ignore[call-arg]

    @relay.connection(relay.ListConnection["Payload"])  # type: ignore
    async def payloads(
            self,
            info: strawberry.Info,
            first: Optional[int] = None,
            after: Optional[str] = None,
    ) -> Iterable["Payload"]:
        from app.graphql.core.pagination import fetch_relay_page  # ← Импорт хелпера

        ctx: GraphQLContext = info.context
        stmt = select(PayloadModel).where(PayloadModel.event_id == self.db_id).order_by(PayloadModel.id.asc())

        return await fetch_relay_page(
            session=ctx.db,
            stmt=stmt,
            first=first,
            after=after,
            model=PayloadModel,
            cursor_fields="id",
            convert=_payload_from_model,
        )

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        ctx: GraphQLContext = info.context
        raw_ids = node_ids
        stmt = select(EventModel).where(EventModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_event_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"Event {rid} not found")
        return [n for n in nodes if n is not None]


@strawberry.type
class Payload(relay.Node):
    """Полезная нагрузка события."""
    db_id: relay.NodeID[int]  # noqa
    event_id: int
    type_id: int
    value: str

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event(self, info: strawberry.Info) -> Optional[Event]:
        ctx: GraphQLContext = info.context
        ev_model = await ctx.db.get(EventModel, self.event_id)
        if ev_model:
            return Event(
                db_id=ev_model.id,  # type: ignore[call-arg]
                client_id=ev_model.client_id,  # type: ignore[call-arg]
                event_type_id=ev_model.event_type_id,  # type: ignore[call-arg]
                trigger_time=ev_model.trigger_time,  # type: ignore[call-arg]
            )
        return None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def payload_type(self, info: strawberry.Info) -> Optional[PayloadType]:
        ctx: GraphQLContext = info.context
        pt_model = await ctx.loaders["payload_type"].load(self.type_id)
        return PayloadType(
            db_id=pt_model.id,
            code_name=pt_model.code_name,
            description=pt_model.description,
            value_type_id=pt_model.value_type_id
        ) if pt_model else None  # type: ignore[call-arg]

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        ctx: GraphQLContext = info.context
        raw_ids = node_ids
        stmt = select(PayloadModel).where(PayloadModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}
        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_payload_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"Payload {rid} not found")
        return [n for n in nodes if n is not None]


@strawberry.type
class DashboardType(relay.Node):
    """Справочник типов дашбордов."""
    db_id: relay.NodeID[int]
    code_name: str
    description: Optional[str] = None

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки DashboardType по глобальным ID."""
        ctx: GraphQLContext = info.context
        raw_ids = node_ids
        stmt = select(DTModel).where(DTModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_dashboard_type_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"DashboardType {rid} not found")
        return [n for n in nodes if n is not None]


@strawberry.type
class Dashboard(relay.Node):
    """Дашборд для отображения статистики."""
    db_id: relay.NodeID[int]
    display_order: int
    event_type_id: int
    dashboard_type_id: int
    title_text: str

    @strawberry.field  # type: ignore[unresolved-reference]
    async def event_type(self, info: strawberry.Info) -> Optional[EventType]:
        """Ленивая загрузка связанного EventType."""
        ctx: GraphQLContext = info.context
        et_model = await ctx.loaders["event_type"].load(self.event_type_id)
        if et_model:
            return _event_type_from_model(et_model)
        return None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def dashboard_type(self, info: strawberry.Info) -> Optional[DashboardType]:
        """Ленивая загрузка связанного EventType."""
        ctx: GraphQLContext = info.context
        dt_model = await ctx.loaders["dashboard_type"].load(self.dashboard_type_id)
        if dt_model:
            return _dashboard_type_from_model(dt_model)
        return None

    @classmethod
    async def resolve_nodes(cls, *, info, node_ids, required=False):
        """Загрузка пачки DashboardType по глобальным ID."""
        ctx: GraphQLContext = info.context
        raw_ids = node_ids
        stmt = select(DashboardModel).where(DashboardModel.id.in_(raw_ids))
        result = {item.id: item for item in (await ctx.db.execute(stmt)).scalars().all()}

        nodes = []
        for rid in raw_ids:
            model = result.get(int(rid))
            if model:
                nodes.append(_dashboard_from_model(model))  # type: ignore[arg-type]
            elif required:
                raise ValueError(f"DashboardType {rid} not found")
        return [n for n in nodes if n is not None]
