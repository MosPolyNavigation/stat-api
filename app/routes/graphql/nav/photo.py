from typing import Optional

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info

from app.constants import VIEW_RIGHT_NAME
from app.models.nav.aud_photo import AudPhoto
from app.models.nav.auditory import Auditory
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

from .types import NavAuditoryPhotoType


@strawberry.type
class NavAuditoryPhotoConnection:
    nodes: list[NavAuditoryPhotoType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class NavAuditoryPhotoFilterInput:
    id: Optional[int] = None
    aud_id: Optional[int] = None
    name: Optional[str] = None
    ext: Optional[str] = None


def _to_nav_auditory_photo(model: AudPhoto) -> NavAuditoryPhotoType:
    from .auditory import _to_nav_auditory_safe

    return NavAuditoryPhotoType(
        id=model.id,
        aud_id=model.aud_id,
        ext=model.ext,
        name=model.name,
        path=model.path,
        link=model.link,
        creation_date=model.creation_date,
        update_date=model.update_date,
        auditory=_to_nav_auditory_safe(model.auditory) if model.auditory else None,
    )


def _to_nav_auditory_photo_safe(model: AudPhoto) -> NavAuditoryPhotoType:
    return NavAuditoryPhotoType(
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


def _apply_photo_filters(statement, filter_data: Optional[NavAuditoryPhotoFilterInput]):
    if not filter_data:
        return statement
    if filter_data.id is not None:
        statement = statement.where(AudPhoto.id == filter_data.id)
    if filter_data.aud_id is not None:
        statement = statement.where(AudPhoto.aud_id == filter_data.aud_id)
    if filter_data.name is not None:
        statement = statement.where(AudPhoto.name == filter_data.name)
    if filter_data.ext is not None:
        statement = statement.where(AudPhoto.ext == filter_data.ext)
    return statement


async def resolve_nav_auditory_photos(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[NavAuditoryPhotoFilterInput] = None,
) -> NavAuditoryPhotoConnection:
    session: AsyncSession = await ensure_nav_permission(info, VIEW_RIGHT_NAME)

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = _apply_photo_filters(
        select(AudPhoto)
        .options(selectinload(AudPhoto.auditory).selectinload(Auditory.typ))
        .order_by(AudPhoto.id),
        filter,
    )
    count_statement = _apply_photo_filters(
        select(func.count()).select_from(AudPhoto),
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

    return NavAuditoryPhotoConnection(
        nodes=[_to_nav_auditory_photo(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )
