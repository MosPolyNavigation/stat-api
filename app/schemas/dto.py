from typing import Optional, List, Tuple
from pydantic import BaseModel, Field


class DataDto(BaseModel):
    locations: List["LocationDto"]
    corpuses: List["CorpusDto"]
    plans: List["PlanDto"]
    rooms: List["RoomDto"]


class LocationDto(BaseModel):
    id: str = Field()
    title: str = Field()
    short: str = Field()
    available: bool = Field()
    address: str = Field()
    crossings: Optional[List[Tuple[str, str, float]]] = Field(default=None)


class CorpusDto(BaseModel):
    id: str
    locationId: str
    title: str
    available: bool
    stairs: Optional[List[List[str]]] = Field(default=None)


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
    wm: Optional[str] = Field(default=None)
    ww: Optional[str] = Field(default=None)
    ws: Optional[str] = Field(default=None)


class GraphDto(BaseModel):
    id: str
    x: float
    y: float
    type: str
    neighborData: List[Tuple[str, float]]


class RoomDto(BaseModel):
    id: str
    planId: str
    type: str
    available: bool
    numberOrTitle: Optional[str] = Field(default=None)
    tabletText: Optional[str] = Field(default=None)
    addInfo: Optional[str] = Field(default=None)
