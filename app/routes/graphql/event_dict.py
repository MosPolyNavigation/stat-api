from datetime import datetime
from typing import List, Optional

import strawberry
from graphql import GraphQLError
from pydantic import BaseModel, ValidationError
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info

from app.models import AllowedPayload, ClientId, EventType, PayloadType, ValueType
from app.routes.graphql.filter_handlers import (
    _create_pagination_info,
    _validated_limit_2,
    _validated_offset,
)
from app.routes.graphql.pagination import PageInfo, PaginationInfo, PaginationInput
from app.routes.graphql.permissions import (
    ensure_stats_create_permission,
    ensure_stats_delete_permission,
    ensure_stats_edit_permission,
    ensure_stats_view_permission,
)
from app.routes.graphql.user_role.types import DeleteResult
from app.scheme import (
    AllowedPayloadRuleCreateRequest,
    AllowedPayloadRuleFilter,
    AllowedPayloadRuleUpdateRequest,
    EventTypeCreateRequest,
    EventTypeFilter,
    EventTypeUpdateRequest,
    PayloadTypeCreateRequest,
    PayloadTypeFilter,
    PayloadTypeUpdateRequest,
    ValueTypeCreateRequest,
    ValueTypeFilter,
    ValueTypeUpdateRequest,
)


@strawberry.type
class ClientIdType:
    id: int
    ident: str
    creation_date: datetime


@strawberry.type
class ValueTypeType:
    id: int
    name: str
    description: Optional[str]


@strawberry.type
class PayloadTypeType:
    id: int
    code_name: str
    description: Optional[str]
    value_type_id: int
    value_type: Optional[ValueTypeType] = None


@strawberry.type
class EventTypeType:
    id: int
    code_name: str
    description: Optional[str]


@strawberry.type
class AllowedPayloadRuleType:
    event_type_id: int
    payload_type_id: int
    event_type: Optional[EventTypeType] = None
    payload_type: Optional[PayloadTypeType] = None


@strawberry.type
class EventTypeConnection:
    nodes: List[EventTypeType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.type
class ValueTypeConnection:
    nodes: List[ValueTypeType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.type
class PayloadTypeConnection:
    nodes: List[PayloadTypeType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.type
class AllowedPayloadRuleConnection:
    nodes: List[AllowedPayloadRuleType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class EventTypeFilterInput:
    id: Optional[int] = None
    code_name: Optional[str] = None


@strawberry.input
class CreateEventTypeInput:
    id: Optional[int] = None
    code_name: str
    description: Optional[str] = None


@strawberry.input
class UpdateEventTypeInput:
    code_name: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class ValueTypeFilterInput:
    id: Optional[int] = None
    name: Optional[str] = None


@strawberry.input
class CreateValueTypeInput:
    id: Optional[int] = None
    name: str
    description: Optional[str] = None


@strawberry.input
class UpdateValueTypeInput:
    name: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class PayloadTypeFilterInput:
    id: Optional[int] = None
    code_name: Optional[str] = None
    value_type_id: Optional[int] = None


@strawberry.input
class CreatePayloadTypeInput:
    id: Optional[int] = None
    code_name: str
    description: Optional[str] = None
    value_type_id: int


@strawberry.input
class UpdatePayloadTypeInput:
    code_name: Optional[str] = None
    description: Optional[str] = None
    value_type_id: Optional[int] = None


@strawberry.input
class AllowedPayloadRuleFilterInput:
    event_type_id: Optional[int] = None
    payload_type_id: Optional[int] = None


@strawberry.input
class CreateAllowedPayloadRuleInput:
    event_type_id: int
    payload_type_id: int


@strawberry.input
class UpdateAllowedPayloadRuleInput:
    event_type_id: int
    payload_type_id: int


def _input_to_dict(data) -> dict:
    return {
        key: value
        for key, value in vars(data).items()
        if not key.startswith("_")
    }


def _validate(schema: type[BaseModel], data) -> BaseModel:
    try:
        return schema.model_validate(_input_to_dict(data))
    except ValidationError as exc:
        raise GraphQLError(str(exc)) from exc


def _to_client_id(model: Optional[ClientId]) -> Optional[ClientIdType]:
    if model is None:
        return None
    return ClientIdType(
        id=model.id,
        ident=model.ident,
        creation_date=model.creation_date,
    )


def _to_value_type(model: Optional[ValueType]) -> Optional[ValueTypeType]:
    if model is None:
        return None
    return ValueTypeType(
        id=model.id,
        name=model.name,
        description=model.description,
    )


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


def _to_event_type(model: Optional[EventType]) -> Optional[EventTypeType]:
    if model is None:
        return None
    return EventTypeType(
        id=model.id,
        code_name=model.code_name,
        description=model.description,
    )


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


async def _paginate(session: AsyncSession, statement, pagination: Optional[PaginationInput]):
    limit = _validated_limit_2(pagination.limit if pagination else None)
    offset = _validated_offset(pagination.offset if pagination else None)
    total = await session.scalar(select(func.count()).select_from(statement.subquery()))
    result = await session.execute(statement.offset(offset).limit(limit))
    rows = result.scalars().all()
    page_info, pagination_info = _create_pagination_info(
        offset,
        limit,
        len(rows),
        total or 0,
    )
    return rows, page_info, pagination_info


def _apply_event_type_filter(statement, filter_data: Optional[EventTypeFilterInput]):
    if filter_data is None:
        return statement
    model = _validate(EventTypeFilter, filter_data)
    if model.id is not None:
        statement = statement.where(EventType.id == model.id)
    if model.code_name is not None:
        statement = statement.where(EventType.code_name == model.code_name)
    return statement


def _apply_value_type_filter(statement, filter_data: Optional[ValueTypeFilterInput]):
    if filter_data is None:
        return statement
    model = _validate(ValueTypeFilter, filter_data)
    if model.id is not None:
        statement = statement.where(ValueType.id == model.id)
    if model.name is not None:
        statement = statement.where(ValueType.name == model.name)
    return statement


def _apply_payload_type_filter(statement, filter_data: Optional[PayloadTypeFilterInput]):
    if filter_data is None:
        return statement
    model = _validate(PayloadTypeFilter, filter_data)
    if model.id is not None:
        statement = statement.where(PayloadType.id == model.id)
    if model.code_name is not None:
        statement = statement.where(PayloadType.code_name == model.code_name)
    if model.value_type_id is not None:
        statement = statement.where(PayloadType.value_type_id == model.value_type_id)
    return statement


def _apply_allowed_payload_filter(
    statement,
    filter_data: Optional[AllowedPayloadRuleFilterInput],
):
    if filter_data is None:
        return statement
    model = _validate(AllowedPayloadRuleFilter, filter_data)
    if model.event_type_id is not None:
        statement = statement.where(AllowedPayload.event_type_id == model.event_type_id)
    if model.payload_type_id is not None:
        statement = statement.where(AllowedPayload.payload_type_id == model.payload_type_id)
    return statement


async def resolve_event_types(
    info: Info,
    filter: Optional[EventTypeFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> EventTypeConnection:
    session = await ensure_stats_view_permission(info)
    statement = _apply_event_type_filter(select(EventType).order_by(EventType.id), filter)
    rows, page_info, pagination_info = await _paginate(session, statement, pagination)
    return EventTypeConnection(
        nodes=[_to_event_type(row) for row in rows],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def resolve_event_type(info: Info, event_type_id: int) -> Optional[EventTypeType]:
    session = await ensure_stats_view_permission(info)
    model = await session.get(EventType, event_type_id)
    return _to_event_type(model)


async def resolve_value_types(
    info: Info,
    filter: Optional[ValueTypeFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> ValueTypeConnection:
    session = await ensure_stats_view_permission(info)
    statement = _apply_value_type_filter(select(ValueType).order_by(ValueType.id), filter)
    rows, page_info, pagination_info = await _paginate(session, statement, pagination)
    return ValueTypeConnection(
        nodes=[_to_value_type(row) for row in rows],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def resolve_value_type(info: Info, value_type_id: int) -> Optional[ValueTypeType]:
    session = await ensure_stats_view_permission(info)
    model = await session.get(ValueType, value_type_id)
    return _to_value_type(model)


async def resolve_payload_types(
    info: Info,
    filter: Optional[PayloadTypeFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> PayloadTypeConnection:
    session = await ensure_stats_view_permission(info)
    statement = (
        select(PayloadType)
        .options(selectinload(PayloadType.value_type))
        .order_by(PayloadType.id)
    )
    statement = _apply_payload_type_filter(statement, filter)
    rows, page_info, pagination_info = await _paginate(session, statement, pagination)
    return PayloadTypeConnection(
        nodes=[_to_payload_type(row) for row in rows],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def resolve_payload_type(
    info: Info,
    payload_type_id: int,
) -> Optional[PayloadTypeType]:
    session = await ensure_stats_view_permission(info)
    model = (
        await session.execute(
            select(PayloadType)
            .options(selectinload(PayloadType.value_type))
            .where(PayloadType.id == payload_type_id)
        )
    ).scalars().first()
    return _to_payload_type(model)


async def resolve_allowed_payload_rules(
    info: Info,
    filter: Optional[AllowedPayloadRuleFilterInput] = None,
    pagination: Optional[PaginationInput] = None,
) -> AllowedPayloadRuleConnection:
    session = await ensure_stats_view_permission(info)
    statement = (
        select(AllowedPayload)
        .options(
            selectinload(AllowedPayload.event_type),
            selectinload(AllowedPayload.payload_type).selectinload(PayloadType.value_type),
        )
        .order_by(AllowedPayload.event_type_id, AllowedPayload.payload_type_id)
    )
    statement = _apply_allowed_payload_filter(statement, filter)
    rows, page_info, pagination_info = await _paginate(session, statement, pagination)
    return AllowedPayloadRuleConnection(
        nodes=[_to_allowed_payload_rule(row) for row in rows],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def resolve_allowed_payload_rule(
    info: Info,
    event_type_id: int,
    payload_type_id: int,
) -> Optional[AllowedPayloadRuleType]:
    session = await ensure_stats_view_permission(info)
    model = (
        await session.execute(
            select(AllowedPayload)
            .options(
                selectinload(AllowedPayload.event_type),
                selectinload(AllowedPayload.payload_type).selectinload(PayloadType.value_type),
            )
            .where(
                AllowedPayload.event_type_id == event_type_id,
                AllowedPayload.payload_type_id == payload_type_id,
            )
        )
    ).scalars().first()
    return _to_allowed_payload_rule(model)


async def _ensure_value_type_exists(session: AsyncSession, value_type_id: int) -> None:
    if await session.get(ValueType, value_type_id) is None:
        raise GraphQLError("Тип значения не найден")


async def _ensure_event_type_exists(session: AsyncSession, event_type_id: int) -> None:
    if await session.get(EventType, event_type_id) is None:
        raise GraphQLError("Тип события не найден")


async def _ensure_payload_type_exists(session: AsyncSession, payload_type_id: int) -> None:
    if await session.get(PayloadType, payload_type_id) is None:
        raise GraphQLError("Тип payload не найден")


async def create_event_type(info: Info, data: CreateEventTypeInput) -> EventTypeType:
    session = await ensure_stats_create_permission(info)
    model_data = _validate(EventTypeCreateRequest, data)
    if model_data.id is not None and await session.get(EventType, model_data.id):
        raise GraphQLError("Тип события с таким id уже существует")
    existing = (
        await session.execute(
            select(EventType).where(EventType.code_name == model_data.code_name)
        )
    ).scalars().first()
    if existing is not None:
        raise GraphQLError("Тип события с таким code_name уже существует")

    model = EventType(**model_data.model_dump(exclude_none=True))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return _to_event_type(model)


async def update_event_type(
    info: Info,
    event_type_id: int,
    data: UpdateEventTypeInput,
) -> EventTypeType:
    session = await ensure_stats_edit_permission(info)
    model_data = _validate(EventTypeUpdateRequest, data)
    model = await session.get(EventType, event_type_id)
    if model is None:
        raise GraphQLError("Тип события не найден")
    for key, value in model_data.model_dump(exclude_none=True).items():
        setattr(model, key, value)
    await session.commit()
    await session.refresh(model)
    return _to_event_type(model)


async def delete_event_type(info: Info, event_type_id: int) -> DeleteResult:
    session = await ensure_stats_delete_permission(info)
    model = await session.get(EventType, event_type_id)
    if model is None:
        raise GraphQLError("Тип события не найден")
    await session.delete(model)
    await session.commit()
    return DeleteResult(success=True, message="Тип события удалён", deleted_id=event_type_id)


async def create_value_type(info: Info, data: CreateValueTypeInput) -> ValueTypeType:
    session = await ensure_stats_create_permission(info)
    model_data = _validate(ValueTypeCreateRequest, data)
    if model_data.id is not None and await session.get(ValueType, model_data.id):
        raise GraphQLError("Тип значения с таким id уже существует")
    model = ValueType(**model_data.model_dump(exclude_none=True))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return _to_value_type(model)


async def update_value_type(
    info: Info,
    value_type_id: int,
    data: UpdateValueTypeInput,
) -> ValueTypeType:
    session = await ensure_stats_edit_permission(info)
    model_data = _validate(ValueTypeUpdateRequest, data)
    model = await session.get(ValueType, value_type_id)
    if model is None:
        raise GraphQLError("Тип значения не найден")
    for key, value in model_data.model_dump(exclude_none=True).items():
        setattr(model, key, value)
    await session.commit()
    await session.refresh(model)
    return _to_value_type(model)


async def delete_value_type(info: Info, value_type_id: int) -> DeleteResult:
    session = await ensure_stats_delete_permission(info)
    model = await session.get(ValueType, value_type_id)
    if model is None:
        raise GraphQLError("Тип значения не найден")
    await session.delete(model)
    await session.commit()
    return DeleteResult(success=True, message="Тип значения удалён", deleted_id=value_type_id)


async def create_payload_type(info: Info, data: CreatePayloadTypeInput) -> PayloadTypeType:
    session = await ensure_stats_create_permission(info)
    model_data = _validate(PayloadTypeCreateRequest, data)
    await _ensure_value_type_exists(session, model_data.value_type_id)
    if model_data.id is not None and await session.get(PayloadType, model_data.id):
        raise GraphQLError("Тип payload с таким id уже существует")
    existing = (
        await session.execute(
            select(PayloadType).where(PayloadType.code_name == model_data.code_name)
        )
    ).scalars().first()
    if existing is not None:
        raise GraphQLError("Тип payload с таким code_name уже существует")

    model = PayloadType(**model_data.model_dump(exclude_none=True))
    session.add(model)
    await session.commit()
    statement = (
        select(PayloadType)
        .options(selectinload(PayloadType.value_type))
        .where(PayloadType.id == model.id)
    )
    return _to_payload_type((await session.execute(statement)).scalars().first())


async def update_payload_type(
    info: Info,
    payload_type_id: int,
    data: UpdatePayloadTypeInput,
) -> PayloadTypeType:
    session = await ensure_stats_edit_permission(info)
    model_data = _validate(PayloadTypeUpdateRequest, data)
    model = await session.get(PayloadType, payload_type_id)
    if model is None:
        raise GraphQLError("Тип payload не найден")
    if model_data.value_type_id is not None:
        await _ensure_value_type_exists(session, model_data.value_type_id)
    for key, value in model_data.model_dump(exclude_none=True).items():
        setattr(model, key, value)
    await session.commit()
    statement = (
        select(PayloadType)
        .options(selectinload(PayloadType.value_type))
        .where(PayloadType.id == payload_type_id)
    )
    return _to_payload_type((await session.execute(statement)).scalars().first())


async def delete_payload_type(info: Info, payload_type_id: int) -> DeleteResult:
    session = await ensure_stats_delete_permission(info)
    model = await session.get(PayloadType, payload_type_id)
    if model is None:
        raise GraphQLError("Тип payload не найден")
    await session.delete(model)
    await session.commit()
    return DeleteResult(success=True, message="Тип payload удалён", deleted_id=payload_type_id)


async def create_allowed_payload_rule(
    info: Info,
    data: CreateAllowedPayloadRuleInput,
) -> AllowedPayloadRuleType:
    session = await ensure_stats_create_permission(info)
    model_data = _validate(AllowedPayloadRuleCreateRequest, data)
    await _ensure_event_type_exists(session, model_data.event_type_id)
    await _ensure_payload_type_exists(session, model_data.payload_type_id)
    existing = await session.get(
        AllowedPayload,
        (model_data.event_type_id, model_data.payload_type_id),
    )
    if existing is not None:
        raise GraphQLError("Правило payload уже существует")

    model = AllowedPayload(**model_data.model_dump())
    session.add(model)
    await session.commit()
    return await resolve_allowed_payload_rule(
        info,
        model.event_type_id,
        model.payload_type_id,
    )


async def update_allowed_payload_rule(
    info: Info,
    event_type_id: int,
    payload_type_id: int,
    data: UpdateAllowedPayloadRuleInput,
) -> AllowedPayloadRuleType:
    session = await ensure_stats_edit_permission(info)
    model_data = _validate(AllowedPayloadRuleUpdateRequest, data)
    existing = await session.get(AllowedPayload, (event_type_id, payload_type_id))
    if existing is None:
        raise GraphQLError("Правило payload не найдено")
    await _ensure_event_type_exists(session, model_data.event_type_id)
    await _ensure_payload_type_exists(session, model_data.payload_type_id)
    duplicate = await session.get(
        AllowedPayload,
        (model_data.event_type_id, model_data.payload_type_id),
    )
    if duplicate is not None and (
        duplicate.event_type_id,
        duplicate.payload_type_id,
    ) != (event_type_id, payload_type_id):
        raise GraphQLError("Правило payload уже существует")

    await session.execute(
        delete(AllowedPayload).where(
            AllowedPayload.event_type_id == event_type_id,
            AllowedPayload.payload_type_id == payload_type_id,
        )
    )
    session.add(AllowedPayload(**model_data.model_dump()))
    await session.commit()
    return await resolve_allowed_payload_rule(
        info,
        model_data.event_type_id,
        model_data.payload_type_id,
    )


async def delete_allowed_payload_rule(
    info: Info,
    event_type_id: int,
    payload_type_id: int,
) -> DeleteResult:
    session = await ensure_stats_delete_permission(info)
    model = await session.get(AllowedPayload, (event_type_id, payload_type_id))
    if model is None:
        raise GraphQLError("Правило payload не найдено")
    await session.delete(model)
    await session.commit()
    return DeleteResult(
        success=True,
        message="Правило payload удалено",
        deleted_id=payload_type_id,
    )
