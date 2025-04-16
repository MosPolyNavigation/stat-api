from pydantic import BaseModel
from typing import List, Tuple
from .dto import GraphDto


class LocationData(BaseModel):
    id: str
    title: str
    short: str
    available: bool
    address: str
    crossings: List[Tuple[str, str, int]]


class CorpusData(BaseModel):
    id: str
    title: str
    available: bool
    location: LocationData
    stairs: List[List[str]]


Id = str
RoomId = Id
CircleId = Id
PlanEntrances = Tuple[RoomId, CircleId]


class PlanData(BaseModel):
    id: str
    floor: int
    available: bool
    wayToSvg: str
    graph: List[GraphDto]
    entrances: List[PlanEntrances]
    corpus: CorpusData
