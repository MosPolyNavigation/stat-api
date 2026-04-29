from typing import Optional, TypeVar

import strawberry
from graphql import GraphQLError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info

from app import scheme
from app.models import AllowedPayload, ClientId, EventType, PayloadType, ValueType

from .pagination import PageInfo, PaginationInfo, PaginationInput
from .permissions import (
    ensure_stats_create_permission,
    ensure_stats_delete_permission,
    ensure_stats_edit_permission,
    ensure_stats_view_permission,
)


T = TypeVar("T")


@strawberry.type
class ClientIdType:
    id: int
    ident: str
    creation_date: str


def _to_client_id(model: Optional[ClientId]) -> Optional[ClientIdType]:
    if model is None:
        return None
    return ClientIdType(
        id=model.id,
        ident=model.ident,
        creation_date=model.creation_date.isoformat(),
    )


@strawberry.type
class ValueTypeType:
    id: int
    name: str
    description: Optional[str]


def _to_value_type(model: Optional[ValueType]) -> Optional[ValueTypeType]:
    if model is None:
        return None
    return ValueTypeType(
        id=model.id,
        name=model.name,
        description=model.description,
    )


@strawberry.type
class PayloadTypeType:
    id: int
    code_name: str
    description: Optional[str]
    value_type_id: int
    value_type: Optional[ValueTypeType]


def _to_payload_type(model: Optional[PayloadType]) -> Optional[PayloadTypeType]:
    if model is None:
        return None
    return PayloadTypeType(
        id=model.id,
        code_name=model.code_name,
        description=model.description,
        value_type_id=model.value_type_id,
        value_type=_to_value_type(model.value_type),
    )


@strawberry.type
class EventTypeType:
    id: int
    code_name: str
    description: Optional[str]


def _to_event_type(model: Optional[EventType]) -> Optional[EventTypeType]:
    if model is None:
        return None
    return EventTypeType(
        id=model.id,
        code_name=model.code_name,
        description=model.description,
    )


@strawberry.type
class AllowedPayloadRuleType:
    event_type_id: int
    payload_type_id: int
    event_type: Optional[EventTypeType]
    payload_type: Optional[PayloadTypeType]


def _to_allowed_payload_rule(
    model: Optional[AllowedPayload],
) -> Optional[AllowedPayloadRuleType]:
    if model is None:
        return None
    return AllowedPayloadRuleType(
        event_type_id=model.event_type_id,
        payload_type_id=model.payload_type_id,
        event_type=_to_event_type(model.event_type),
        payload_type=_to_payload_type(model.payload_type),
    )


@strawberry.type
class EventTypeConnection:
    nodes: list[EventTypeType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.type
class PayloadTypeConnection:
    nodes: list[PayloadTypeType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.type
class ValueTypeConnection:
    nodes: list[ValueTypeType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.type
class AllowedPayloadRuleConnection:
    nodes: list[AllowedPayloadRuleType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class EventTypeFilterInput:
    id: Optional[int] = None
    code_name: Optional[str] = None


@strawberry.input
class EventTypeInput:
    id: Optional[int] = None
    code_name: str
    description: Optional[str] = None


@strawberry.input
class EventTypeUpdateInput:
    code_name: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class ValueTypeFilterInput:
    id: Optional[int] = None
    name: Optional[str] = None


@strawberry.input
class ValueTypeInput:
    id: Optional[int] = None
    name: str
    description: Optional[str] = None


@strawberry.input
class ValueTypeUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class PayloadTypeFilterInput:
    id: Optional[int] = None
    code_name: Optional[str] = None
    value_type_id: Optional[int] = None


@strawberry.input
class PayloadTypeInput:
    id: Optional[int] = None
    code_name: str
    value_type_id: int
    description: Optional[str] = None


@strawberry.input
class PayloadTypeUpdateInput:
    code_name: Optional[str] = None
    value_type_id: Optional[int] = None
    description: Optional[str] = None


@strawberry.input
class AllowedPayloadRuleFilterInput:
    event_type_id: Optional[int] = None
    payload_type_id: Optional[int] = None


@strawberry.input
class AllowedPayloadRuleInput:
    event_type_id: int
    payload_type_id: int


@strawberry.input
class AllowedPayloadRuleUpdateInput:
    new_event_type_id: int
    new_payload_type_id: int


def _pagination_values(pagination: Optional[PaginationInput]) -> tuple[int, int]:
    limit = pagination.limit if pagination and pagination.limit is not None else 10
    offset = pagination.offset if pagination and pagination.offset is not None else 0
    return max(limit, 0), max(offset, 0)


def _page_info(total: int, limit: int, offset: int) -> tuple[PageInfo, PaginationInfo]:
    current_page = offset // limit + 1 if limit else 1
    total_pages = (total + limit - 1) // limit if limit else 1
    return (
        PageInfo(
            has_previous_page=offset > 0,
            has_next_page=offset + limit < total if limit else False,
            start_cursor=str(offset) if total else None,
            end_cursor=str(min(offset + limit, total)) if total else None,
        ),
        PaginationInfo(
            total_count=total,
            current_page=current_page,
            total_pages=total_pages,
        ),
    )


async def _exists(session: AsyncSession, model: type[T], item_id: int) -> bool:
    return (
        await session.execute(select(model).where(model.id == item_id))
    ).scalar_one_or_none() is not None


async def resolve_event_types(
    info: Info,
    filter: Optional[EventTypeFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> EventTypeConnection:
    session = await ensure_stats_view_permission(info)
    data = scheme.EventTypeFilter(**(filter.__dict__ if filter else {}))
    statement = select(EventType).order_by(EventType.id.asc())
    count_statement = select(func.count()).select_from(EventType)
    if data.id is not None:
        statement = statement.where(EventType.id == data.id)
        count_statement = count_statement.where(EventType.id == data.id)
    if data.code_name:
        statement = statement.where(EventType.code_name == data.code_name)
        count_statement = count_statement.where(EventType.code_name == data.code_name)
    limit, offset = _pagination_values(pagination)
    total = int((await session.execute(count_statement)).scalar_one())
    records = (await session.execute(statement.offset(offset).limit(limit))).scalars().all()
    page_info, pagination_info = _page_info(total, limit, offset)
    return EventTypeConnection(
        nodes=[_to_event_type(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def resolve_value_types(
    info: Info,
    filter: Optional[ValueTypeFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> ValueTypeConnection:
    session = await ensure_stats_view_permission(info)
    data = scheme.ValueTypeFilter(**(filter.__dict__ if filter else {}))
    statement = select(ValueType).order_by(ValueType.id.asc())
    count_statement = select(func.count()).select_from(ValueType)
    if data.id is not None:
        statement = statement.where(ValueType.id == data.id)
        count_statement = count_statement.where(ValueType.id == data.id)
    if data.name:
        statement = statement.where(ValueType.name == data.name)
        count_statement = count_statement.where(ValueType.name == data.name)
    limit, offset = _pagination_values(pagination)
    total = int((await session.execute(count_statement)).scalar_one())
    records = (await session.execute(statement.offset(offset).limit(limit))).scalars().all()
    page_info, pagination_info = _page_info(total, limit, offset)
    return ValueTypeConnection(
        nodes=[_to_value_type(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def resolve_payload_types(
    info: Info,
    filter: Optional[PayloadTypeFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> PayloadTypeConnection:
    session = await ensure_stats_view_permission(info)
    data = scheme.PayloadTypeFilter(**(filter.__dict__ if filter else {}))
    statement = select(PayloadType).options(selectinload(PayloadType.value_type)).order_by(PayloadType.id.asc())
    count_statement = select(func.count()).select_from(PayloadType)
    if data.id is not None:
        statement = statement.where(PayloadType.id == data.id)
        count_statement = count_statement.where(PayloadType.id == data.id)
    if data.code_name:
        statement = statement.where(PayloadType.code_name == data.code_name)
        count_statement = count_statement.where(PayloadType.code_name == data.code_name)
    if data.value_type_id is not None:
        statement = statement.where(PayloadType.value_type_id == data.value_type_id)
        count_statement = count_statement.where(PayloadType.value_type_id == data.value_type_id)
    limit, offset = _pagination_values(pagination)
    total = int((await session.execute(count_statement)).scalar_one())
    records = (await session.execute(statement.offset(offset).limit(limit))).scalars().all()
    page_info, pagination_info = _page_info(total, limit, offset)
    return PayloadTypeConnection(
        nodes=[_to_payload_type(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def resolve_allowed_payload_rules(
    info: Info,
    filter: Optional[AllowedPayloadRuleFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> AllowedPayloadRuleConnection:
    session = await ensure_stats_view_permission(info)
    data = scheme.AllowedPayloadRuleFilter(**(filter.__dict__ if filter else {}))
    statement = (
        select(AllowedPayload)
        .options(
            selectinload(AllowedPayload.event_type),
            selectinload(AllowedPayload.payload_type).selectinload(PayloadType.value_type),
        )
        .order_by(AllowedPayload.event_type_id.asc(), AllowedPayload.payload_type_id.asc())
    )
    count_statement = select(func.count()).select_from(AllowedPayload)
    if data.event_type_id is not None:
        statement = statement.where(AllowedPayload.event_type_id == data.event_type_id)
        count_statement = count_statement.where(AllowedPayload.event_type_id == data.event_type_id)
    if data.payload_type_id is not None:
        statement = statement.where(AllowedPayload.payload_type_id == data.payload_type_id)
        count_statement = count_statement.where(AllowedPayload.payload_type_id == data.payload_type_id)
    limit, offset = _pagination_values(pagination)
    total = int((await session.execute(count_statement)).scalar_one())
    records = (await session.execute(statement.offset(offset).limit(limit))).scalars().all()
    page_info, pagination_info = _page_info(total, limit, offset)
    return AllowedPayloadRuleConnection(
        nodes=[_to_allowed_payload_rule(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_event_type(info: Info, data: EventTypeInput) -> EventTypeType:
    session = await ensure_stats_create_permission(info)
    payload = scheme.EventTypeCreate(**data.__dict__)
    item = EventType(id=payload.id, code_name=payload.code_name, description=payload.description)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _to_event_type(item)


async def update_event_type(info: Info, event_type_id: int, data: EventTypeUpdateInput) -> EventTypeType:
    session = await ensure_stats_edit_permission(info)
    payload = scheme.EventTypeUpdate(**data.__dict__)
    item = (await session.execute(select(EventType).where(EventType.id == event_type_id))).scalar_one_or_none()
    if item is None:
        raise GraphQLError(f"EventType {event_type_id} not found")
    if payload.code_name is not None:
        item.code_name = payload.code_name
    if data.description is not None:
        item.description = payload.description
    await session.commit()
    await session.refresh(item)
    return _to_event_type(item)


async def delete_event_type(info: Info, event_type_id: int) -> bool:
    session = await ensure_stats_delete_permission(info)
    item = (await session.execute(select(EventType).where(EventType.id == event_type_id))).scalar_one_or_none()
    if item is None:
        raise GraphQLError(f"EventType {event_type_id} not found")
    await session.delete(item)
    await session.commit()
    return True


async def create_value_type(info: Info, data: ValueTypeInput) -> ValueTypeType:
    session = await ensure_stats_create_permission(info)
    payload = scheme.ValueTypeCreate(**data.__dict__)
    item = ValueType(id=payload.id, name=payload.name, description=payload.description)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _to_value_type(item)


async def update_value_type(info: Info, value_type_id: int, data: ValueTypeUpdateInput) -> ValueTypeType:
    session = await ensure_stats_edit_permission(info)
    payload = scheme.ValueTypeUpdate(**data.__dict__)
    item = (await session.execute(select(ValueType).where(ValueType.id == value_type_id))).scalar_one_or_none()
    if item is None:
        raise GraphQLError(f"ValueType {value_type_id} not found")
    if payload.name is not None:
        item.name = payload.name
    if data.description is not None:
        item.description = payload.description
    await session.commit()
    await session.refresh(item)
    return _to_value_type(item)


async def delete_value_type(info: Info, value_type_id: int) -> bool:
    session = await ensure_stats_delete_permission(info)
    item = (await session.execute(select(ValueType).where(ValueType.id == value_type_id))).scalar_one_or_none()
    if item is None:
        raise GraphQLError(f"ValueType {value_type_id} not found")
    await session.delete(item)
    await session.commit()
    return True


async def create_payload_type(info: Info, data: PayloadTypeInput) -> PayloadTypeType:
    session = await ensure_stats_create_permission(info)
    payload = scheme.PayloadTypeCreate(**data.__dict__)
    if not await _exists(session, ValueType, payload.value_type_id):
        raise GraphQLError(f"ValueType {payload.value_type_id} not found")
    item = PayloadType(
        id=payload.id,
        code_name=payload.code_name,
        value_type_id=payload.value_type_id,
        description=payload.description,
    )
    session.add(item)
    await session.commit()
    item = (
        await session.execute(
            select(PayloadType)
            .options(selectinload(PayloadType.value_type))
            .where(PayloadType.id == item.id)
        )
    ).scalar_one()
    return _to_payload_type(item)


async def update_payload_type(info: Info, payload_type_id: int, data: PayloadTypeUpdateInput) -> PayloadTypeType:
    session = await ensure_stats_edit_permission(info)
    payload = scheme.PayloadTypeUpdate(**data.__dict__)
    item = (
        await session.execute(
            select(PayloadType)
            .options(selectinload(PayloadType.value_type))
            .where(PayloadType.id == payload_type_id)
        )
    ).scalar_one_or_none()
    if item is None:
        raise GraphQLError(f"PayloadType {payload_type_id} not found")
    if payload.value_type_id is not None:
        if not await _exists(session, ValueType, payload.value_type_id):
            raise GraphQLError(f"ValueType {payload.value_type_id} not found")
        item.value_type_id = payload.value_type_id
    if payload.code_name is not None:
        item.code_name = payload.code_name
    if data.description is not None:
        item.description = payload.description
    await session.commit()
    await session.refresh(item, ["value_type"])
    return _to_payload_type(item)


async def delete_payload_type(info: Info, payload_type_id: int) -> bool:
    session = await ensure_stats_delete_permission(info)
    item = (await session.execute(select(PayloadType).where(PayloadType.id == payload_type_id))).scalar_one_or_none()
    if item is None:
        raise GraphQLError(f"PayloadType {payload_type_id} not found")
    await session.delete(item)
    await session.commit()
    return True


async def create_allowed_payload_rule(info: Info, data: AllowedPayloadRuleInput) -> AllowedPayloadRuleType:
    session = await ensure_stats_create_permission(info)
    payload = scheme.AllowedPayloadRuleCreate(**data.__dict__)
    if not await _exists(session, EventType, payload.event_type_id):
        raise GraphQLError(f"EventType {payload.event_type_id} not found")
    if not await _exists(session, PayloadType, payload.payload_type_id):
        raise GraphQLError(f"PayloadType {payload.payload_type_id} not found")
    item = AllowedPayload(event_type_id=payload.event_type_id, payload_type_id=payload.payload_type_id)
    session.add(item)
    await session.commit()
    item = (
        await session.execute(
            select(AllowedPayload)
            .options(
                selectinload(AllowedPayload.event_type),
                selectinload(AllowedPayload.payload_type).selectinload(PayloadType.value_type),
            )
            .where(AllowedPayload.event_type_id == payload.event_type_id)
            .where(AllowedPayload.payload_type_id == payload.payload_type_id)
        )
    ).scalar_one()
    return _to_allowed_payload_rule(item)


async def update_allowed_payload_rule(
    info: Info,
    event_type_id: int,
    payload_type_id: int,
    data: AllowedPayloadRuleUpdateInput,
) -> AllowedPayloadRuleType:
    session = await ensure_stats_edit_permission(info)
    payload = scheme.AllowedPayloadRuleUpdate(
        event_type_id=event_type_id,
        payload_type_id=payload_type_id,
        **data.__dict__,
    )
    item = (
        await session.execute(
            select(AllowedPayload)
            .where(AllowedPayload.event_type_id == payload.event_type_id)
            .where(AllowedPayload.payload_type_id == payload.payload_type_id)
        )
    ).scalar_one_or_none()
    if item is None:
        raise GraphQLError("Правило допустимого payload не найдено")
    if not await _exists(session, EventType, payload.new_event_type_id):
        raise GraphQLError(f"EventType {payload.new_event_type_id} not found")
    if not await _exists(session, PayloadType, payload.new_payload_type_id):
        raise GraphQLError(f"PayloadType {payload.new_payload_type_id} not found")
    await session.delete(item)
    await session.flush()
    replacement = AllowedPayload(
        event_type_id=payload.new_event_type_id,
        payload_type_id=payload.new_payload_type_id,
    )
    session.add(replacement)
    await session.commit()
    replacement = (
        await session.execute(
            select(AllowedPayload)
            .options(
                selectinload(AllowedPayload.event_type),
                selectinload(AllowedPayload.payload_type).selectinload(PayloadType.value_type),
            )
            .where(AllowedPayload.event_type_id == payload.new_event_type_id)
            .where(AllowedPayload.payload_type_id == payload.new_payload_type_id)
        )
    ).scalar_one()
    return _to_allowed_payload_rule(replacement)


async def delete_allowed_payload_rule(
    info: Info,
    event_type_id: int,
    payload_type_id: int,
) -> bool:
    session = await ensure_stats_delete_permission(info)
    item = (
        await session.execute(
            select(AllowedPayload)
            .where(AllowedPayload.event_type_id == event_type_id)
            .where(AllowedPayload.payload_type_id == payload_type_id)
        )
    ).scalar_one_or_none()
    if item is None:
        raise GraphQLError("Правило допустимого payload не найдено")
    await session.delete(item)
    await session.commit()
    return True
