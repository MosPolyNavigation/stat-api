from typing import Optional

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info

from app.constants import VIEW_RIGHT_NAME
from app.models.dod.aud_photo import DodAudPhoto
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

from .types import DodNavAuditoryPhotoType


@strawberry.type
class DodNavAuditoryPhotoConnection:
    nodes: list[DodNavAuditoryPhotoType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class DodNavAuditoryPhotoFilterInput:
    id: Optional[int] = None
    aud_id: Optional[int] = None
    name: Optional[str] = None
    ext: Optional[str] = None


def _to_dod_nav_auditory_photo(model: DodAudPhoto) -> DodNavAuditoryPhotoType:
    from .auditory import _to_dod_nav_auditory_safe

    return DodNavAuditoryPhotoType(
        id=model.id,
        aud_id=model.aud_id,
        ext=model.ext,
        name=model.name,
        path=model.path,
        link=model.link,
        creation_date=model.creation_date,
        update_date=model.update_date,
        auditory=_to_dod_nav_auditory_safe(model.auditory) if model.auditory else None,
    )


def _to_dod_nav_auditory_photo_safe(model: DodAudPhoto) -> DodNavAuditoryPhotoType:
    return DodNavAuditoryPhotoType(
        id=model.id,
        aud_id=model.aud_id,
        ext=model.ext,
        name=model.name,
        path=model.path,
        link=model.link,
        creation_date=model.creation_date,
        update_date=model.update_date,
        auditory=None,
    )


def _apply_photo_filters(
    statement,
    filter_data: Optional[DodNavAuditoryPhotoFilterInput],
):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(DodAudPhoto.id == filter_data.id)
    if filter_data.aud_id is not None:
        statement = statement.where(DodAudPhoto.aud_id == filter_data.aud_id)
    if filter_data.name is not None:
        statement = statement.where(DodAudPhoto.name == filter_data.name)
    if filter_data.ext is not None:
        statement = statement.where(DodAudPhoto.ext == filter_data.ext)
    return statement


async def resolve_dod_nav_auditory_photos(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[DodNavAuditoryPhotoFilterInput] = None,
) -> DodNavAuditoryPhotoConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_photo_filters(
        select(DodAudPhoto)
        .options(selectinload(DodAudPhoto.auditory))
        .order_by(DodAudPhoto.id),
        filter,
    )
    count_statement = _apply_photo_filters(
        select(func.count()).select_from(DodAudPhoto),
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

    return DodNavAuditoryPhotoConnection(
        nodes=[_to_dod_nav_auditory_photo(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )
