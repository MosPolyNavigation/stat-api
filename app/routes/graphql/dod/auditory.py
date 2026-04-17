from typing import Optional

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info

from app.constants import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
)
from app.models.dod.auditory import DodAuditory
from app.routes.graphql.filter_handlers import (
    _create_pagination_info,
    _validated_limit_2,
    _validated_offset,
)
from app.routes.graphql.pagination import (
    PageInfo,
    PaginationInfo,
    PaginationInput,
)
from app.routes.graphql.permissions import ensure_nav_permission

from .common import get_or_error
from .types import DodNavAuditoryType


@strawberry.type
class DodNavAuditoryConnection:
    nodes: list[DodNavAuditoryType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class DodNavAuditoryInput:
    id_sys: str
    type_id: int
    ready: bool
    plan_id: int
    name: str
    text_from_sign: Optional[str] = None
    additional_info: Optional[str] = None
    comments: Optional[str] = None
    link: Optional[str] = None


@strawberry.input
class DodNavAuditoryUpdateInput:
    id_sys: Optional[str] = None
    type_id: Optional[int] = None
    ready: Optional[bool] = None
    plan_id: Optional[int] = None
    name: Optional[str] = None
    text_from_sign: Optional[str] = None
    additional_info: Optional[str] = None
    comments: Optional[str] = None
    link: Optional[str] = None


@strawberry.input
class DodNavAuditoryFilterInput:
    id: Optional[int] = None
    id_sys: Optional[str] = None
    plan_id: Optional[int] = None
    type_id: Optional[int] = None
    ready: Optional[bool] = None
    name: Optional[str] = None


def _to_dod_nav_auditory(model: DodAuditory) -> DodNavAuditoryType:
    from .nav_type import _to_dod_nav_type
    from .photo import _to_dod_nav_auditory_photo_safe
    from .plan import _to_dod_nav_plan_safe

    return DodNavAuditoryType(
        id=model.id,
        id_sys=model.id_sys,
        type_id=model.type_id,
        ready=model.ready,
        plan_id=model.plan_id,
        name=model.name,
        text_from_sign=model.text_from_sign,
        additional_info=model.additional_info,
        comments=model.comments,
        link=model.link,
        type=_to_dod_nav_type(model.typ) if model.typ else None,
        plan=_to_dod_nav_plan_safe(model.plans) if model.plans else None,
        photos=[
            _to_dod_nav_auditory_photo_safe(photo)
            for photo in model.photos
        ] if model.photos else None,
    )


def _to_dod_nav_auditory_safe(model: DodAuditory) -> DodNavAuditoryType:
    return DodNavAuditoryType(
        id=model.id,
        id_sys=model.id_sys,
        type_id=model.type_id,
        ready=model.ready,
        plan_id=model.plan_id,
        name=model.name,
        text_from_sign=model.text_from_sign,
        additional_info=model.additional_info,
        comments=model.comments,
        link=model.link,
        type=None,
        plan=None,
        photos=None,
    )


def _apply_auditory_filters(
    statement,
    filter_data: Optional[DodNavAuditoryFilterInput],
):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(DodAuditory.id == filter_data.id)
    if filter_data.id_sys is not None:
        statement = statement.where(DodAuditory.id_sys == filter_data.id_sys)
    if filter_data.plan_id is not None:
        statement = statement.where(DodAuditory.plan_id == filter_data.plan_id)
    if filter_data.type_id is not None:
        statement = statement.where(DodAuditory.type_id == filter_data.type_id)
    if filter_data.ready is not None:
        statement = statement.where(DodAuditory.ready == filter_data.ready)
    if filter_data.name is not None:
        statement = statement.where(DodAuditory.name == filter_data.name)
    return statement


async def resolve_dod_nav_auditories(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[DodNavAuditoryFilterInput] = None,
) -> DodNavAuditoryConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_auditory_filters(
        select(DodAuditory)
        .options(
            selectinload(DodAuditory.typ),
            selectinload(DodAuditory.plans),
            selectinload(DodAuditory.photos),
        )
        .order_by(DodAuditory.id),
        filter,
    )
    count_statement = _apply_auditory_filters(
        select(func.count()).select_from(DodAuditory),
        filter,
    )

    total_count = (await session.execute(count_statement)).scalar() or 0

    if offset > 0:
        statement = statement.offset(offset)
    if limit > 0:
        statement = statement.limit(limit)

    records = (await session.execute(statement)).scalars().all()
    page_info, pagination_info = _create_pagination_info(
        total_count=total_count,
        offset=offset,
        limit=limit,
        records_count=len(records),
    )

    return DodNavAuditoryConnection(
        nodes=[_to_dod_nav_auditory(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )


async def create_dod_nav_auditory(
    info: Info,
    data: DodNavAuditoryInput,
) -> DodNavAuditoryType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    auditory = DodAuditory(
        id_sys=data.id_sys,
        type_id=data.type_id,
        ready=data.ready,
        plan_id=data.plan_id,
        name=data.name,
        text_from_sign=data.text_from_sign,
        additional_info=data.additional_info,
        comments=data.comments,
        link=data.link,
    )
    session.add(auditory)
    await session.commit()
    await session.refresh(auditory)
    return _to_dod_nav_auditory_safe(auditory)


async def update_dod_nav_auditory(
    info: Info,
    id: int,
    data: DodNavAuditoryUpdateInput,
) -> DodNavAuditoryType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    auditory = await get_or_error(session, DodAuditory, id, "auditory")
    if data.id_sys is not None:
        auditory.id_sys = data.id_sys
    if data.type_id is not None:
        auditory.type_id = data.type_id
    if data.ready is not None:
        auditory.ready = data.ready
    if data.plan_id is not None:
        auditory.plan_id = data.plan_id
    if data.name is not None:
        auditory.name = data.name
    if data.text_from_sign is not None:
        auditory.text_from_sign = data.text_from_sign
    if data.additional_info is not None:
        auditory.additional_info = data.additional_info
    if data.comments is not None:
        auditory.comments = data.comments
    if data.link is not None:
        auditory.link = data.link
    await session.commit()
    await session.refresh(auditory)
    return _to_dod_nav_auditory_safe(auditory)


async def delete_dod_nav_auditory(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    auditory = await get_or_error(session, DodAuditory, id, "auditory")
    await session.delete(auditory)
    await session.commit()
    return True
