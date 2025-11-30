from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.nav.location import Location
from app.routes.graphql.permissions import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
    ensure_nav_permission,
)
from .common import get_or_error


@strawberry.type(name="NavLocation")
class NavLocationType:
    id: int
    id_sys: str
    name: str
    short: str
    ready: bool
    address: str
    metro: str
    crossings: Optional[str]
    comments: Optional[str]


@strawberry.input
class NavLocationInput:
    id_sys: str
    name: str
    short: str
    ready: bool
    address: str
    metro: str
    comments: Optional[str] = None


@strawberry.input
class NavLocationUpdateInput:
    id_sys: Optional[str] = None
    name: Optional[str] = None
    short: Optional[str] = None
    ready: Optional[bool] = None
    address: Optional[str] = None
    metro: Optional[str] = None
    comments: Optional[str] = None


def _to_nav_location(model: Location) -> NavLocationType:
    return NavLocationType(
        id=model.id,
        id_sys=model.id_sys,
        name=model.name,
        short=model.short,
        ready=model.ready,
        address=model.address,
        metro=model.metro,
        crossings=model.crossings,
        comments=model.comments,
    )


async def resolve_nav_locations(info: Info, id: Optional[int] = None, id_sys: Optional[str] = None) -> list[NavLocationType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Location).order_by(Location.id)
    if id is not None:
        statement = statement.where(Location.id == id)
    if id_sys is not None:
        statement = statement.where(Location.id_sys == id_sys)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_location(record) for record in records]


async def create_nav_location(info: Info, data: NavLocationInput) -> NavLocationType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    location = Location(
        id_sys=data.id_sys,
        name=data.name,
        short=data.short,
        ready=data.ready,
        address=data.address,
        metro=data.metro,
        crossings=None,
        comments=data.comments,
    )
    session.add(location)
    await session.commit()
    await session.refresh(location)
    return _to_nav_location(location)


async def update_nav_location(info: Info, id: int, data: NavLocationUpdateInput) -> NavLocationType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    location = await get_or_error(session, Location, id, "location")
    if data.id_sys is not None:
        location.id_sys = data.id_sys
    if data.name is not None:
        location.name = data.name
    if data.short is not None:
        location.short = data.short
    if data.ready is not None:
        location.ready = data.ready
    if data.address is not None:
        location.address = data.address
    if data.metro is not None:
        location.metro = data.metro
    if data.comments is not None:
        location.comments = data.comments
    await session.commit()
    await session.refresh(location)
    return _to_nav_location(location)


async def delete_nav_location(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    location = await get_or_error(session, Location, id, "location")
    await session.delete(location)
    await session.commit()
    return True
