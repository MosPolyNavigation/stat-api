from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import strawberry


@strawberry.type(name="DodNavLocation")
class DodNavLocationType:
    id: int
    id_sys: str
    name: str
    short: str
    ready: bool
    address: str
    metro: str
    crossings: Optional[str]
    comments: Optional[str]


@strawberry.type(name="DodNavCampus")
class DodNavCampusType:
    id: int
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    stair_groups: Optional[str]
    comments: Optional[str]
    location: Optional[DodNavLocationType] = None


@strawberry.type(name="DodNavFloor")
class DodNavFloorType:
    id: int
    name: int


@strawberry.type(name="DodNavStatic")
class DodNavStaticType:
    id: int
    ext: str
    path: str
    name: str
    link: str
    creation_date: Optional[datetime]
    update_date: Optional[datetime]


@strawberry.type(name="DodNavType")
class DodNavTypeType:
    id: int
    name: str


@strawberry.type(name="DodNavPlan")
class DodNavPlanType:
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
    campus: Optional[DodNavCampusType] = None
    floor: Optional[DodNavFloorType] = None
    svg: Optional[DodNavStaticType] = None


@strawberry.type(name="DodNavAuditoryPhoto")
class DodNavAuditoryPhotoType:
    id: int
    aud_id: int
    ext: str
    name: str
    path: str
    link: str
    creation_date: Optional[datetime]
    update_date: Optional[datetime]
    auditory: Optional["DodNavAuditoryType"] = None


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
    type: Optional[DodNavTypeType] = None
    plan: Optional[DodNavPlanType] = None
    photos: Optional[List[DodNavAuditoryPhotoType]] = None
