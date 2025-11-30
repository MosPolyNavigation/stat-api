from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.nav.static import Static
from app.routes.graphql.permissions import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
    ensure_nav_permission,
)
from .common import get_or_error


@strawberry.type(name="NavStatic")
class NavStaticType:
    id: int
    ext: str
    path: str
    name: str
    link: str
    creation_date: Optional[str]
    update_date: Optional[str]


@strawberry.input
class NavStaticInput:
    ext: str
    path: str
    name: str
    link: str


@strawberry.input
class NavStaticUpdateInput:
    ext: Optional[str] = None
    path: Optional[str] = None
    name: Optional[str] = None
    link: Optional[str] = None


def _to_nav_static(model: Static) -> NavStaticType:
    return NavStaticType(
        id=model.id,
        ext=model.ext,
        path=model.path,
        name=model.name,
        link=model.link,
        creation_date=model.creation_date,
        update_date=model.update_date,
    )


async def resolve_nav_statics(info: Info, id: Optional[int] = None, name: Optional[str] = None) -> list[NavStaticType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Static).order_by(Static.id)
    if id is not None:
        statement = statement.where(Static.id == id)
    if name is not None:
        statement = statement.where(Static.name == name)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_static(record) for record in records]


async def create_nav_static(info: Info, data: NavStaticInput) -> NavStaticType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    static = Static(
        ext=data.ext,
        path=data.path,
        name=data.name,
        link=data.link,
    )
    session.add(static)
    await session.commit()
    await session.refresh(static)
    return _to_nav_static(static)


async def update_nav_static(info: Info, id: int, data: NavStaticUpdateInput) -> NavStaticType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    static = await get_or_error(session, Static, id, "static file")
    if data.ext is not None:
        static.ext = data.ext
    if data.path is not None:
        static.path = data.path
    if data.name is not None:
        static.name = data.name
    if data.link is not None:
        static.link = data.link
    await session.commit()
    await session.refresh(static)
    return _to_nav_static(static)


async def delete_nav_static(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    static = await get_or_error(session, Static, id, "static file")
    await session.delete(static)
    await session.commit()
    return True
