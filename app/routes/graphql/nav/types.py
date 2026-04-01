from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import strawberry


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


@strawberry.type(name="NavCampus")
class NavCampusType:
    id: int
    id_sys: str
    loc_id: int
    name: str
    ready: bool
    stair_groups: Optional[str]
    comments: Optional[str]
    location: Optional[NavLocationType] = None


@strawberry.type(name="NavFloor")
class NavFloorType:
    id: int
    name: int


@strawberry.type(name="NavStatic")
class NavStaticType:
    id: int
    ext: str
    path: str
    name: str
    link: str
    creation_date: Optional[datetime]
    update_date: Optional[datetime]


@strawberry.type(name="NavType")
class NavTypeType:
    id: int
    name: str


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
    campus: Optional[NavCampusType] = None
    floor: Optional[NavFloorType] = None
    svg: Optional[NavStaticType] = None


@strawberry.type(name="NavAuditoryPhoto")
class NavAuditoryPhotoType:
    id: int
    aud_id: int
    ext: str
    name: str
    path: str
    link: str
    creation_date: Optional[datetime]
    update_date: Optional[datetime]
    auditory: Optional["NavAuditoryType"] = None


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
    type: Optional[NavTypeType] = None
    plan: Optional[NavPlanType] = None
    photos: Optional[List[NavAuditoryPhotoType]] = None
