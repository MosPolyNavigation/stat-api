from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.dod.floor import Floor
from app.routes.graphql.permissions import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
    ensure_nav_permission,
)
from .common import get_or_error


@strawberry.type(name="DodNavFloor")
class DodNavFloorType:
    id: int
    name: int


@strawberry.input
class DodNavFloorInput:
    name: int


@strawberry.input
class DodNavFloorUpdateInput:
    name: Optional[int] = None


def _to_dod_nav_floor(model: Floor) -> DodNavFloorType:
    return DodNavFloorType(id=model.id, name=model.name)


async def resolve_dod_nav_floors(info: Info, id: Optional[int] = None, name: Optional[int] = None) -> list[DodNavFloorType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Floor).order_by(Floor.id)
    if id is not None:
        statement = statement.where(Floor.id == id)
    if name is not None:
        statement = statement.where(Floor.name == name)
    records = (await session.execute(statement)).scalars().all()
    return [_to_dod_nav_floor(record) for record in records]


async def create_dod_nav_floor(info: Info, data: DodNavFloorInput) -> DodNavFloorType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    floor = Floor(name=data.name)
    session.add(floor)
    await session.commit()
    await session.refresh(floor)
    return _to_dod_nav_floor(floor)


async def update_dod_nav_floor(info: Info, id: int, data: DodNavFloorUpdateInput) -> DodNavFloorType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    floor = await get_or_error(session, Floor, id, "floor")
    if data.name is not None:
        floor.name = data.name
    await session.commit()
    await session.refresh(floor)
    return _to_dod_nav_floor(floor)


async def delete_dod_nav_floor(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    floor = await get_or_error(session, Floor, id, "floor")
    await session.delete(floor)
    await session.commit()
    return True

