from sqlalchemy import select
from typing import Optional
from datetime import datetime
import strawberry

from app.graphql.core.context import GraphQLContext
from app.graphql.core.filters import apply_filters
from app.graphql.core.ordering import apply_order_by
from app.graphql.core.pagination import Connection, PaginationInput, paginate_query
from app.graphql.domains.navigation.inputs import (
    NavCampusFilterInput,
    NavCampusOrderByInput, NavPlanFilterInput, NavPlanOrderByInput, NavAuditoryFilterInput, NavAuditoryOrderByInput,
    NavAuditoryPhotoFilterInput, NavAuditoryPhotoOrderByInput
)
from app.models.nav.location import Location as LModel
from app.models.nav.corpus import Corpus as CModel
from app.models.nav.floor import Floor as FModel
from app.models.nav.types import Type as NTModel
from app.models.nav.plan import Plan as PModel
from app.models.nav.auditory import Auditory as AModel
from app.models.nav.aud_photo import AudPhoto as APModel
from app.models.nav.static import Static as SModel


# =============================================================================
# Helpers: Конвертеры моделей → типы
# =============================================================================
def _location_from_model(m: LModel) -> "NavLocation":
    return NavLocation(
        id=m.id,
        id_sys=m.id_sys,
        name=m.name,
        short=m.short,
        ready=m.ready,
        address=m.address,
        metro=m.metro,
        crossings=m.crossings,
        comments=m.comments,
    )


def _campus_from_model(m: CModel) -> "NavCampus":
    return NavCampus(
        id=m.id,
        id_sys=m.id_sys,
        loc_id=m.loc_id,
        name=m.name,
        ready=m.ready,
        stair_groups=m.stair_groups,
        comments=m.comments,
    )


def _floor_from_model(m: FModel) -> "NavFloor":
    return NavFloor(id=m.id, name=m.name)


def _type_from_model(m: NTModel) -> "NavType":
    return NavType(id=m.id, name=m.name)


def _plan_from_model(m: PModel) -> "NavPlan":
    return NavPlan(
        id=m.id,
        id_sys=m.id_sys,
        cor_id=m.cor_id,
        floor_id=m.floor_id,
        ready=m.ready,
        entrances=m.entrances,
        graph=m.graph,
        svg_id=m.svg_id,
        nearest_entrance=m.nearest_entrance,
        nearest_man_wc=m.nearest_man_wc,
        nearest_woman_wc=m.nearest_woman_wc,
        nearest_shared_wc=m.nearest_shared_wc,
    )


def _auditory_from_model(m: AModel) -> "NavAuditory":
    return NavAuditory(
        id=m.id,
        id_sys=m.id_sys,
        type_id=m.type_id,
        ready=m.ready,
        plan_id=m.plan_id,
        name=m.name,
        text_from_sign=m.text_from_sign,
        additional_info=m.additional_info,
        comments=m.comments,
        link=m.link,
    )


def _aud_photo_from_model(m: APModel) -> "NavAuditoryPhoto":
    return NavAuditoryPhoto(
        id=m.id,
        aud_id=m.aud_id,
        ext=m.ext,
        name=m.name,
        path=m.path,
        link=m.link,
        creation_date=m.creation_date,
        update_date=m.update_date,
    )


def _static_from_model(m: SModel) -> "NavStatic":
    return NavStatic(
        id=m.id,
        ext=m.ext,
        path=m.path,
        name=m.name,
        link=m.link,
        creation_date=m.creation_date,
        update_date=m.update_date,
    )


@strawberry.type
class NavLocation:
    id: int
    id_sys: str
    name: str
    short: str
    ready: bool
    address: str
    metro: str
    crossings: Optional[str]
    comments: Optional[str]

    @strawberry.field()
    async def campuses(
        self,
        info: strawberry.Info,  # noqa
        pagination: Optional[PaginationInput] = None,
        filter: Optional[NavCampusFilterInput] = None,
        order_by: Optional[NavCampusOrderByInput] = None,
    ) -> Connection["NavCampus"]:
        ctx: GraphQLContext = info.context
        stmt = select(CModel).where(CModel.loc_id == self.id)
        if filter:
            stmt = apply_filters(stmt, CModel, filter)
        if order_by:
            stmt = apply_order_by(stmt, CModel, order_by)
        if pagination is None:
            pagination = PaginationInput(page=1, page_size=10)  # noqa
        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_campus_from_model,
        )


@strawberry.type
class NavCampus:
    id: int
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    stair_groups: Optional[str]
    comments: Optional[str]

    @strawberry.field  # type: ignore[unresolved-reference]
    async def location(self, info: strawberry.Info) -> Optional[NavLocation]:
        ctx: GraphQLContext = info.context
        nl_model = await ctx.loaders["nav_location"].load(self.loc_id)
        return _location_from_model(nl_model) if nl_model else None

    @strawberry.field()
    async def plans(
        self,
        info: strawberry.Info,  # noqa
        pagination: Optional[PaginationInput] = None,
        filter: Optional[NavPlanFilterInput] = None,
        order_by: Optional[NavPlanOrderByInput] = None,
    ) -> Connection["NavPlan"]:
        ctx: GraphQLContext = info.context
        stmt = select(PModel).where(PModel.cor_id == self.id)
        if filter:
            stmt = apply_filters(stmt, PModel, filter)
        if order_by:
            stmt = apply_order_by(stmt, PModel, order_by)
        if pagination is None:
            pagination = PaginationInput(page=1, page_size=10)  # noqa
        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_plan_from_model,
        )


@strawberry.type
class NavFloor:
    id: int
    name: int


@strawberry.type
class NavType:
    id: int
    name: str


@strawberry.type
class NavPlan:
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

    @strawberry.field  # type: ignore[unresolved-reference]
    async def campus(self, info: strawberry.Info) -> Optional[NavCampus]:
        ctx: GraphQLContext = info.context
        nc_model = await ctx.loaders["nav_campus"].load(self.cor_id)
        return _campus_from_model(nc_model) if nc_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def floor(self, info: strawberry.Info) -> Optional[NavFloor]:
        ctx: GraphQLContext = info.context
        nf_model = await ctx.loaders["nav_floor"].load(self.floor_id)
        return _floor_from_model(nf_model) if nf_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def svg(self, info: strawberry.Info) -> Optional["NavStatic"]:
        ctx: GraphQLContext = info.context
        if self.svg_id is None:
            return None
        ns_model = await ctx.loaders["nav_static"].load(self.svg_id)
        return _static_from_model(ns_model) if ns_model else None

    @strawberry.field()
    async def auditories(
        self,
        info: strawberry.Info,  # noqa
        pagination: Optional[PaginationInput] = None,
        filter: Optional[NavAuditoryFilterInput] = None,
        order_by: Optional[NavAuditoryOrderByInput] = None,
    ) -> Connection["NavAuditory"]:
        ctx: GraphQLContext = info.context
        stmt = select(AModel).where(AModel.plan_id == self.id)
        if filter:
            stmt = apply_filters(stmt, AModel, filter)
        if order_by:
            stmt = apply_order_by(stmt, AModel, order_by)
        if pagination is None:
            pagination = PaginationInput(page=1, page_size=10)  # noqa
        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_auditory_from_model,
        )


@strawberry.type
class NavAuditory:
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

    @strawberry.field  # type: ignore[unresolved-reference]
    async def type(self, info: strawberry.Info) -> Optional[NavType]:
        ctx: GraphQLContext = info.context
        nt_model = await ctx.loaders["nav_type"].load(self.type_id)
        return _type_from_model(nt_model) if nt_model else None

    @strawberry.field  # type: ignore[unresolved-reference]
    async def plan(self, info: strawberry.Info) -> Optional[NavPlan]:
        ctx: GraphQLContext = info.context
        np_model = await ctx.loaders["nav_plan"].load(self.plan_id)
        return _plan_from_model(np_model) if np_model else None

    @strawberry.field()
    async def photos(
        self,
        info: strawberry.Info,  # noqa
        pagination: Optional[PaginationInput] = None,
        filter: Optional[NavAuditoryPhotoFilterInput] = None,
        order_by: Optional[NavAuditoryPhotoOrderByInput] = None,
    ) -> Connection["NavAuditoryPhoto"]:
        ctx: GraphQLContext = info.context
        stmt = select(APModel).where(APModel.aud_id == self.id)
        if filter:
            stmt = apply_filters(stmt, APModel, filter)
        if order_by:
            stmt = apply_order_by(stmt, APModel, order_by)
        if pagination is None:
            pagination = PaginationInput(page=1, page_size=10)  # noqa
        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_aud_photo_from_model,
        )


@strawberry.type
class NavAuditoryPhoto:
    id: int
    aud_id: int
    ext: str
    name: str
    path: str
    link: str
    creation_date: Optional[datetime]
    update_date: Optional[datetime]

    @strawberry.field  # type: ignore[unresolved-reference]
    async def auditory(self, info: strawberry.Info) -> Optional[NavAuditory]:
        ctx: GraphQLContext = info.context
        na_model = await ctx.loaders["nav_auditory"].load(self.aud_id)
        return _auditory_from_model(na_model) if na_model else None


@strawberry.type
class NavStatic:
    id: int
    ext: str
    path: str
    name: str
    link: str
    creation_date: Optional[datetime]
    update_date: Optional[datetime]

    @strawberry.field()
    async def plans(
        self,
        info: strawberry.Info,  # noqa
        pagination: Optional[PaginationInput] = None,
        filter: Optional[NavPlanFilterInput] = None,
        order_by: Optional[NavPlanOrderByInput] = None,
    ) -> Connection["NavPlan"]:
        ctx: GraphQLContext = info.context
        stmt = select(PModel).where(PModel.svg_id == self.id)
        if filter:
            stmt = apply_filters(stmt, PModel, filter)
        if order_by:
            stmt = apply_order_by(stmt, PModel, order_by)
        if pagination is None:
            pagination = PaginationInput(page=1, page_size=10)  # noqa
        return await paginate_query(
            session=ctx.db,
            stmt=stmt,
            pagination=pagination,
            convert=_plan_from_model,
        )
