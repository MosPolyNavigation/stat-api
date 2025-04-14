from typing import Optional, List, Tuple
from pydantic import BaseModel


class DataDto(BaseModel):
    locations: List["LocationDto"]
    corpuses: List["CorpusDto"]
    plans: List["PlanDto"]
    rooms: List["RoomDto"]


class LocationDto(BaseModel):
    id: str
    title: str
    short: str
    available: bool
    address: str
    crossings: Optional[List[Tuple[str, str, int]]]

class CorpusDto(BaseModel):
    id: str
    locationId: str
    title: str
    available: bool
    stairs: Optional[List[str]]


class PlanDto(BaseModel):
    id: str
    corpusId: str
    floor: str
    available: bool
    wayToSvg: str
    graph: List["GraphDto"]
    entrances: List[Tuple[str, str]]
    nearest: "NearestDto"


class NearestDto(BaseModel):
    enter: str
    wm: Optional[str]
    ww: Optional[str]
    ws: Optional[str]


class GraphDto(BaseModel):
    id: str
    x: int
    y: int
    type: str
    neighborData: List[Tuple[str, int]]


class RoomDto(BaseModel):
    id: str
    planId: str
    type: str
    available: bool
    numberOrTitle: Optional[str]
    tabletText: Optional[str]
    addInfo: Optional[str]
