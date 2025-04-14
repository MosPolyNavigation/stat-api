from pydantic import BaseModel
from . import CorpusData, GraphDto
from typing import List, Tuple

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
