from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.dod.auditory import DodAuditory
from app.routes.graphql.permissions import CREATE_RIGHT_NAME, DELETE_RIGHT_NAME, EDIT_RIGHT_NAME, VIEW_RIGHT_NAME, ensure_nav_permission
from .common import get_or_error


@strawberry.type(name="DodNavAuditory")
class DodNavAuditoryType:
    id: int
    id_sys: str
    type_id: int
    ready: bool
    plan_id: int
    name: str
    text_from_sign: Optional[str]
    additional_info: Optional[str]
    comments: Optional[str]
    link: Optional[str]


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


def _to_dod_nav_auditory(model: DodAuditory) -> DodNavAuditoryType:
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
    )


async def resolve_dod_nav_auditories(
    info: Info,
    id: Optional[int] = None,
    id_sys: Optional[str] = None,
    plan_id: Optional[int] = None,
    type_id: Optional[int] = None,
) -> list[DodNavAuditoryType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(DodAuditory).order_by(DodAuditory.id)
    if id is not None:
        statement = statement.where(DodAuditory.id == id)
    if id_sys is not None:
        statement = statement.where(DodAuditory.id_sys == id_sys)
    if plan_id is not None:
        statement = statement.where(DodAuditory.plan_id == plan_id)
    if type_id is not None:
        statement = statement.where(DodAuditory.type_id == type_id)
    records = (await session.execute(statement)).scalars().all()
    return [_to_dod_nav_auditory(record) for record in records]


async def create_dod_nav_auditory(info: Info, data: DodNavAuditoryInput) -> DodNavAuditoryType:
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
    return _to_dod_nav_auditory(auditory)


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
    return _to_dod_nav_auditory(auditory)


async def delete_dod_nav_auditory(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    auditory = await get_or_error(session, DodAuditory, id, "auditory")
    await session.delete(auditory)
    await session.commit()
    return True



