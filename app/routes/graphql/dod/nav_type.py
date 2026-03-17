from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.dod.types import DodType
from app.routes.graphql.permissions import CREATE_RIGHT_NAME, DELETE_RIGHT_NAME, EDIT_RIGHT_NAME, VIEW_RIGHT_NAME, ensure_nav_permission
from .common import get_or_error


@strawberry.type(name="DodNavType")
class DodNavTypeType:
    id: int
    name: str


@strawberry.input
class DodNavTypeInput:
    name: str


@strawberry.input
class DodNavTypeUpdateInput:
    name: Optional[str] = None


def _to_dod_nav_type(model: DodType) -> DodNavTypeType:
    return DodNavTypeType(id=model.id, name=model.name)


async def resolve_dod_nav_types(
    info: Info,
    id: Optional[int] = None,
    name: Optional[str] = None,
) -> list[DodNavTypeType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(DodType).order_by(DodType.id)
    if id is not None:
        statement = statement.where(DodType.id == id)
    if name is not None:
        statement = statement.where(DodType.name == name)
    records = (await session.execute(statement)).scalars().all()
    return [_to_dod_nav_type(record) for record in records]


async def create_dod_nav_type(info: Info, data: DodNavTypeInput) -> DodNavTypeType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    nav_type = DodType(name=data.name)
    session.add(nav_type)
    await session.commit()
    await session.refresh(nav_type)
    return _to_dod_nav_type(nav_type)


async def update_dod_nav_type(
    info: Info,
    id: int,
    data: DodNavTypeUpdateInput,
) -> DodNavTypeType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    nav_type = await get_or_error(session, DodType, id, "type")
    if data.name is not None:
        nav_type.name = data.name
    await session.commit()
    await session.refresh(nav_type)
    return _to_dod_nav_type(nav_type)


async def delete_dod_nav_type(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    nav_type = await get_or_error(session, DodType, id, "type")
    await session.delete(nav_type)
    await session.commit()
    return True



