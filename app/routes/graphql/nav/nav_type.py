from typing import Optional
import strawberry
from sqlalchemy import select
from strawberry import Info
from app.models.nav.types import Type as NavTypeModel
from app.routes.graphql.permissions import (
    CREATE_RIGHT_NAME,
    DELETE_RIGHT_NAME,
    EDIT_RIGHT_NAME,
    VIEW_RIGHT_NAME,
    ensure_nav_permission,
)
from .common import get_or_error


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


async def resolve_nav_types(info: Info, id: Optional[int] = None, name: Optional[str] = None) -> list[NavTypeType]:
    session = await ensure_nav_permission(info, VIEW_RIGHT_NAME)
    statement = select(NavTypeModel).order_by(NavTypeModel.id)
    if id is not None:
        statement = statement.where(NavTypeModel.id == id)
    if name is not None:
        statement = statement.where(NavTypeModel.name == name)
    records = (await session.execute(statement)).scalars().all()
    return [_to_nav_type(record) for record in records]


async def create_nav_type(info: Info, data: NavTypeInput) -> NavTypeType:
    session = await ensure_nav_permission(info, CREATE_RIGHT_NAME)
    nav_type = NavTypeModel(name=data.name)
    session.add(nav_type)
    await session.commit()
    await session.refresh(nav_type)
    return _to_nav_type(nav_type)


async def update_nav_type(info: Info, id: int, data: NavTypeUpdateInput) -> NavTypeType:
    session = await ensure_nav_permission(info, EDIT_RIGHT_NAME)
    nav_type = await get_or_error(session, NavTypeModel, id, "type")
    if data.name is not None:
        nav_type.name = data.name
    await session.commit()
    await session.refresh(nav_type)
    return _to_nav_type(nav_type)


async def delete_nav_type(info: Info, id: int) -> bool:
    session = await ensure_nav_permission(info, DELETE_RIGHT_NAME)
    nav_type = await get_or_error(session, NavTypeModel, id, "type")
    await session.delete(nav_type)
    await session.commit()
    return True
