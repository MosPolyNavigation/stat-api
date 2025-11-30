from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.nav.corpus import Corpus
from app.routes.graphql.permissions import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
    ensure_nav_permission,
)
from .common import get_or_error


@strawberry.type(name="NavCampus")
class NavCampusType:
    id: int
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    stair_groups: Optional[str]
    comments: Optional[str]


@strawberry.input
class NavCampusInput:
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    comments: Optional[str] = None


@strawberry.input
class NavCampusUpdateInput:
    id_sys: Optional[str] = None
    loc_id: Optional[int] = None
    name: Optional[str] = None
    ready: Optional[bool] = None
    comments: Optional[str] = None


def _to_nav_campus(model: Corpus) -> NavCampusType:
    return NavCampusType(
        id=model.id,
        id_sys=model.id_sys,
        loc_id=model.loc_id,
        name=model.name,
        ready=model.ready,
        stair_groups=model.stair_groups,
        comments=model.comments,
    )


async def resolve_nav_campuses(info: Info, id: Optional[int] = None, id_sys: Optional[str] = None, loc_id: Optional[int] = None) -> list[NavCampusType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Corpus).order_by(Corpus.id)
    if id is not None:
        statement = statement.where(Corpus.id == id)
    if id_sys is not None:
        statement = statement.where(Corpus.id_sys == id_sys)
    if loc_id is not None:
        statement = statement.where(Corpus.loc_id == loc_id)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_campus(record) for record in records]


async def create_nav_campus(info: Info, data: NavCampusInput) -> NavCampusType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    campus = Corpus(
        id_sys=data.id_sys,
        loc_id=data.loc_id,
        name=data.name,
        ready=data.ready,
        stair_groups=None,
        comments=data.comments,
    )
    session.add(campus)
    await session.commit()
    await session.refresh(campus)
    return _to_nav_campus(campus)


async def update_nav_campus(info: Info, id: int, data: NavCampusUpdateInput) -> NavCampusType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    campus = await get_or_error(session, Corpus, id, "campus")
    if data.id_sys is not None:
        campus.id_sys = data.id_sys
    if data.loc_id is not None:
        campus.loc_id = data.loc_id
    if data.name is not None:
        campus.name = data.name
    if data.ready is not None:
        campus.ready = data.ready
    if data.comments is not None:
        campus.comments = data.comments
    await session.commit()
    await session.refresh(campus)
    return _to_nav_campus(campus)


async def delete_nav_campus(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    campus = await get_or_error(session, Corpus, id, "campus")
    await session.delete(campus)
    await session.commit()
    return True
