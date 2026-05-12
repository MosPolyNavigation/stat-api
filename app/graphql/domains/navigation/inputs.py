from typing import Optional, List
import strawberry
from app.graphql.core.filters import BaseFilterInput, StringFilterInput, IntFilterInput, BooleanFilterInput
from app.graphql.core.ordering import BaseOrderByInput, OrderDir


# =============================================================================
# Filters
# =============================================================================
@strawberry.input
class NavLocationFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    id_sys: Optional[StringFilterInput] = None
    name: Optional[StringFilterInput] = None
    short: Optional[StringFilterInput] = None
    ready: Optional[BooleanFilterInput] = None
    and_: Optional[List["NavLocationFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavLocationFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavLocationFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class NavCampusFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    id_sys: Optional[StringFilterInput] = None
    loc_id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    ready: Optional[BooleanFilterInput] = None
    and_: Optional[List["NavCampusFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavCampusFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavCampusFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class NavFloorFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    name: Optional[IntFilterInput] = None
    and_: Optional[List["NavFloorFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavFloorFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavFloorFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class NavTypeFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    and_: Optional[List["NavTypeFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavTypeFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavTypeFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class NavPlanFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    id_sys: Optional[StringFilterInput] = None
    cor_id: Optional[IntFilterInput] = None
    floor_id: Optional[IntFilterInput] = None
    ready: Optional[BooleanFilterInput] = None
    svg_id: Optional[IntFilterInput] = None
    and_: Optional[List["NavPlanFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavPlanFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavPlanFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class NavAuditoryFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    id_sys: Optional[StringFilterInput] = None
    plan_id: Optional[IntFilterInput] = None
    type_id: Optional[IntFilterInput] = None
    ready: Optional[BooleanFilterInput] = None
    name: Optional[StringFilterInput] = None
    and_: Optional[List["NavAuditoryFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavAuditoryFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavAuditoryFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class NavAuditoryPhotoFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    aud_id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    ext: Optional[StringFilterInput] = None
    and_: Optional[List["NavAuditoryPhotoFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavAuditoryPhotoFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavAuditoryPhotoFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class NavStaticFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    ext: Optional[StringFilterInput] = None
    link: Optional[StringFilterInput] = None
    and_: Optional[List["NavStaticFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["NavStaticFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["NavStaticFilterInput"] = strawberry.field(name="not", default=None)


# =============================================================================
# OrderBy
# =============================================================================
@strawberry.input
class NavLocationOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavLocationOrderByInput"] = None


@strawberry.input
class NavCampusOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavCampusOrderByInput"] = None


@strawberry.input
class NavFloorOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavFloorOrderByInput"] = None


@strawberry.input
class NavTypeOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavTypeOrderByInput"] = None


@strawberry.input
class NavPlanOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavPlanOrderByInput"] = None


@strawberry.input
class NavAuditoryOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavAuditoryOrderByInput"] = None


@strawberry.input
class NavAuditoryPhotoOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavAuditoryPhotoOrderByInput"] = None


@strawberry.input
class NavStaticOrderByInput(BaseOrderByInput):
    id: Optional[OrderDir] = None
    name: Optional[OrderDir] = None
    then_by: Optional["NavStaticOrderByInput"] = None


# =============================================================================
# Mutation Inputs
# =============================================================================
@strawberry.input
class NavLocationInput:
    id_sys: str
    name: str
    short: str
    ready: bool
    address: str
    metro: str
    comments: Optional[str] = None
    crossings: Optional[str] = None


@strawberry.input
class NavLocationUpdateInput:
    id_sys: Optional[str] = None
    name: Optional[str] = None
    short: Optional[str] = None
    ready: Optional[bool] = None
    address: Optional[str] = None
    metro: Optional[str] = None
    comments: Optional[str] = None
    crossings: Optional[str] = None


@strawberry.input
class NavCampusInput:
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    comments: Optional[str] = None
    stair_groups: Optional[str] = None


@strawberry.input
class NavCampusUpdateInput:
    id_sys: Optional[str] = None
    loc_id: Optional[int] = None
    name: Optional[str] = None
    ready: Optional[bool] = None
    comments: Optional[str] = None
    stair_groups: Optional[str] = None


@strawberry.input
class NavFloorInput:
    name: int


@strawberry.input
class NavFloorUpdateInput:
    name: Optional[int] = None


@strawberry.input
class NavTypeInput:
    name: str


@strawberry.input
class NavTypeUpdateInput:
    name: Optional[str] = None


@strawberry.input
class NavPlanInput:
    id_sys: str
    cor_id: int
    floor_id: int
    ready: bool
    entrances: Optional[str] = None
    graph: Optional[str] = None
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
    entrances: Optional[str] = None
    graph: Optional[str] = None
    nearest_entrance: Optional[str] = None
    nearest_man_wc: Optional[str] = None
    nearest_woman_wc: Optional[str] = None
    nearest_shared_wc: Optional[str] = None


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
