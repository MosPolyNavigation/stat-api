from datetime import datetime
from typing import Optional, TypeVar
import strawberry
from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info

from app.models.nav.auditory import Auditory
from app.models.nav.corpus import Corpus
from app.models.nav.floor import Floor
from app.models.nav.location import Location
from app.models.nav.plan import Plan
from app.models.nav.static import Static
from app.models.nav.types import Type as NavTypeModel
from .permissions import (
    ensure_nav_permission,
    VIEW_RIGHT_NAME,
    CREATE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    DELETE_RIGHT_NAME,
)

DEFAULT_PLAN_ENTRANCES = "[]"
DEFAULT_PLAN_GRAPH = "{}"

ModelT = TypeVar("ModelT", Floor, Location, Corpus, Plan, Static, NavTypeModel, Auditory)


def _raise_not_found(entity: str) -> None:
    raise GraphQLError(f"Сущность {entity} не найдена")


async def _get_or_error(session: AsyncSession, model: type[ModelT], entity_id: int, name: str) -> ModelT:
    instance = await session.get(model, entity_id)
    if instance is None:
        _raise_not_found(name)
    return instance


@strawberry.type(name="NavFloor")
class NavFloorType:
    id: int
    name: int


@strawberry.input
class NavFloorInput:
    name: int


@strawberry.input
class NavFloorUpdateInput:
    name: Optional[int] = None


def _to_nav_floor(model: Floor) -> NavFloorType:
    return NavFloorType(id=model.id, name=model.name)


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


@strawberry.type(name="NavPlan")
class NavPlanType:
    id: int
    id_sys: str
    cor_id: int
    floor_id: int
    ready: bool
    entrances: str
    graph: str
    svg_id: Optional[int]
    nearest_entrance: Optional[str]
    nearest_man_wc: Optional[str]
    nearest_woman_wc: Optional[str]
    nearest_shared_wc: Optional[str]


@strawberry.input
class NavPlanInput:
    id_sys: str
    cor_id: int
    floor_id: int
    ready: bool
    nearest_entrance: Optional[str] = None
    nearest_man_wc: Optional[str] = None
    nearest_woman_wc: Optional[str] = None
    nearest_shared_wc: Optional[str] = None


@strawberry.input
class NavPlanUpdateInput:
    id_sys: Optional[str] = None
    cor_id: Optional[int] = None
    floor_id: Optional[int] = None
    ready: Optional[bool] = None
    nearest_entrance: Optional[str] = None
    nearest_man_wc: Optional[str] = None
    nearest_woman_wc: Optional[str] = None
    nearest_shared_wc: Optional[str] = None


def _to_nav_plan(model: Plan) -> NavPlanType:
    return NavPlanType(
        id=model.id,
        id_sys=model.id_sys,
        cor_id=model.cor_id,
        floor_id=model.floor_id,
        ready=model.ready,
        entrances=model.entrances,
        graph=model.graph,
        svg_id=model.svg_id,
        nearest_entrance=model.nearest_entrance,
        nearest_man_wc=model.nearest_man_wc,
        nearest_woman_wc=model.nearest_woman_wc,
        nearest_shared_wc=model.nearest_shared_wc,
    )


@strawberry.type(name="NavStatic")
class NavStaticType:
    id: int
    ext: str
    path: str
    name: str
    link: str
    creation_date: datetime
    update_date: datetime


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


@strawberry.type(name="NavType")
class NavTypeType:
    id: int
    name: str


@strawberry.input
class NavTypeInput:
    name: str


@strawberry.input
class NavTypeUpdateInput:
    name: Optional[str] = None


def _to_nav_type(model: NavTypeModel) -> NavTypeType:
    return NavTypeType(id=model.id, name=model.name)


@strawberry.type(name="NavAuditory")
class NavAuditoryType:
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
    photo_id: Optional[int]


@strawberry.input
class NavAuditoryInput:
    id_sys: str
    type_id: int
    ready: bool
    plan_id: int
    name: str
    text_from_sign: Optional[str] = None
    additional_info: Optional[str] = None
    comments: Optional[str] = None
    link: Optional[str] = None
    photo_id: Optional[int] = None


@strawberry.input
class NavAuditoryUpdateInput:
    id_sys: Optional[str] = None
    type_id: Optional[int] = None
    ready: Optional[bool] = None
    plan_id: Optional[int] = None
    name: Optional[str] = None
    text_from_sign: Optional[str] = None
    additional_info: Optional[str] = None
    comments: Optional[str] = None
    link: Optional[str] = None
    photo_id: Optional[int] = None


def _to_nav_auditory(model: Auditory) -> NavAuditoryType:
    return NavAuditoryType(
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
        photo_id=model.photo_id,
    )


async def resolve_nav_floors(info: Info, id: Optional[int] = None, name: Optional[int] = None) -> list[NavFloorType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Floor).order_by(Floor.id)
    if id is not None:
        statement = statement.where(Floor.id == id)
    if name is not None:
        statement = statement.where(Floor.name == name)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_floor(record) for record in records]


async def resolve_nav_locations(info: Info, id: Optional[int] = None, id_sys: Optional[str] = None) -> list[NavLocationType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Location).order_by(Location.id)
    if id is not None:
        statement = statement.where(Location.id == id)
    if id_sys is not None:
        statement = statement.where(Location.id_sys == id_sys)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_location(record) for record in records]


async def resolve_nav_campuses(
    info: Info,
    id: Optional[int] = None,
    id_sys: Optional[str] = None,
    loc_id: Optional[int] = None,
) -> list[NavCampusType]:
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


async def resolve_nav_plans(
    info: Info,
    id: Optional[int] = None,
    id_sys: Optional[str] = None,
    cor_id: Optional[int] = None,
    floor_id: Optional[int] = None,
) -> list[NavPlanType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Plan).order_by(Plan.id)
    if id is not None:
        statement = statement.where(Plan.id == id)
    if id_sys is not None:
        statement = statement.where(Plan.id_sys == id_sys)
    if cor_id is not None:
        statement = statement.where(Plan.cor_id == cor_id)
    if floor_id is not None:
        statement = statement.where(Plan.floor_id == floor_id)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_plan(record) for record in records]


async def resolve_nav_statics(info: Info, id: Optional[int] = None, name: Optional[str] = None) -> list[NavStaticType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Static).order_by(Static.id)
    if id is not None:
        statement = statement.where(Static.id == id)
    if name is not None:
        statement = statement.where(Static.name == name)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_static(record) for record in records]


async def resolve_nav_types(info: Info, id: Optional[int] = None, name: Optional[str] = None) -> list[NavTypeType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(NavTypeModel).order_by(NavTypeModel.id)
    if id is not None:
        statement = statement.where(NavTypeModel.id == id)
    if name is not None:
        statement = statement.where(NavTypeModel.name == name)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_type(record) for record in records]


async def resolve_nav_auditories(
    info: Info,
    id: Optional[int] = None,
    id_sys: Optional[str] = None,
    plan_id: Optional[int] = None,
    type_id: Optional[int] = None,
) -> list[NavAuditoryType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(Auditory).order_by(Auditory.id)
    if id is not None:
        statement = statement.where(Auditory.id == id)
    if id_sys is not None:
        statement = statement.where(Auditory.id_sys == id_sys)
    if plan_id is not None:
        statement = statement.where(Auditory.plan_id == plan_id)
    if type_id is not None:
        statement = statement.where(Auditory.type_id == type_id)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_auditory(record) for record in records]


async def create_nav_floor(info: Info, data: NavFloorInput) -> NavFloorType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    floor = Floor(name=data.name)
    session.add(floor)
    await session.commit()
    await session.refresh(floor)
    return _to_nav_floor(floor)


async def update_nav_floor(info: Info, id: int, data: NavFloorUpdateInput) -> NavFloorType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    floor = await _get_or_error(session, Floor, id, "floor")
    if data.name is not None:
        floor.name = data.name
    await session.commit()
    await session.refresh(floor)
    return _to_nav_floor(floor)


async def delete_nav_floor(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    floor = await _get_or_error(session, Floor, id, "floor")
    await session.delete(floor)
    await session.commit()
    return True


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
    location = await _get_or_error(session, Location, id, "location")
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
    location = await _get_or_error(session, Location, id, "location")
    await session.delete(location)
    await session.commit()
    return True


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
    campus = await _get_or_error(session, Corpus, id, "campus")
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
    campus = await _get_or_error(session, Corpus, id, "campus")
    await session.delete(campus)
    await session.commit()
    return True


async def create_nav_plan(info: Info, data: NavPlanInput) -> NavPlanType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    plan = Plan(
        id_sys=data.id_sys,
        cor_id=data.cor_id,
        floor_id=data.floor_id,
        ready=data.ready,
        entrances=DEFAULT_PLAN_ENTRANCES,
        graph=DEFAULT_PLAN_GRAPH,
        svg_id=None,
        nearest_entrance=data.nearest_entrance,
        nearest_man_wc=data.nearest_man_wc,
        nearest_woman_wc=data.nearest_woman_wc,
        nearest_shared_wc=data.nearest_shared_wc,
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return _to_nav_plan(plan)


async def update_nav_plan(info: Info, id: int, data: NavPlanUpdateInput) -> NavPlanType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    plan = await _get_or_error(session, Plan, id, "plan")
    if data.id_sys is not None:
        plan.id_sys = data.id_sys
    if data.cor_id is not None:
        plan.cor_id = data.cor_id
    if data.floor_id is not None:
        plan.floor_id = data.floor_id
    if data.ready is not None:
        plan.ready = data.ready
    if data.nearest_entrance is not None:
        plan.nearest_entrance = data.nearest_entrance
    if data.nearest_man_wc is not None:
        plan.nearest_man_wc = data.nearest_man_wc
    if data.nearest_woman_wc is not None:
        plan.nearest_woman_wc = data.nearest_woman_wc
    if data.nearest_shared_wc is not None:
        plan.nearest_shared_wc = data.nearest_shared_wc
    await session.commit()
    await session.refresh(plan)
    return _to_nav_plan(plan)


async def delete_nav_plan(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    plan = await _get_or_error(session, Plan, id, "plan")
    await session.delete(plan)
    await session.commit()
    return True


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
    static = await _get_or_error(session, Static, id, "static file")
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
    static = await _get_or_error(session, Static, id, "static file")
    await session.delete(static)
    await session.commit()
    return True


async def create_nav_type(info: Info, data: NavTypeInput) -> NavTypeType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    nav_type = NavTypeModel(name=data.name)
    session.add(nav_type)
    await session.commit()
    await session.refresh(nav_type)
    return _to_nav_type(nav_type)


async def update_nav_type(info: Info, id: int, data: NavTypeUpdateInput) -> NavTypeType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    nav_type = await _get_or_error(session, NavTypeModel, id, "type")
    if data.name is not None:
        nav_type.name = data.name
    await session.commit()
    await session.refresh(nav_type)
    return _to_nav_type(nav_type)


async def delete_nav_type(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    nav_type = await _get_or_error(session, NavTypeModel, id, "type")
    await session.delete(nav_type)
    await session.commit()
    return True


async def create_nav_auditory(info: Info, data: NavAuditoryInput) -> NavAuditoryType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    auditory = Auditory(
        id_sys=data.id_sys,
        type_id=data.type_id,
        ready=data.ready,
        plan_id=data.plan_id,
        name=data.name,
        text_from_sign=data.text_from_sign,
        additional_info=data.additional_info,
        comments=data.comments,
        link=data.link,
        photo_id=data.photo_id,
    )
    session.add(auditory)
    await session.commit()
    await session.refresh(auditory)
    return _to_nav_auditory(auditory)


async def update_nav_auditory(info: Info, id: int, data: NavAuditoryUpdateInput) -> NavAuditoryType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    auditory = await _get_or_error(session, Auditory, id, "auditory")
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
    if data.photo_id is not None:
        auditory.photo_id = data.photo_id
    await session.commit()
    await session.refresh(auditory)
    return _to_nav_auditory(auditory)


async def delete_nav_auditory(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    auditory = await _get_or_error(session, Auditory, id, "auditory")
    await session.delete(auditory)
    await session.commit()
    return True
