from typing import Any
from pydantic import BaseModel

# Пара [id точки, подпись/номер]
type Entrance = list[str]
type Entrances = list[Entrance]

# Элемент neighborData: [id_соседа, дистанция]
type Neighbor = tuple[str, float]
type NeighborData = list[Neighbor]


class Node(BaseModel):
    """
    Элемент графа из поля "graph" в {loc}{plan}.json:

    """
    id: str
    x: float
    y: float
    type: str
    neighborData: NeighborData


type Graph = list[Node]
type Spaces = list[Any]

class PlanNav(BaseModel):
    """
    Формат одного плана
    """
    planName: str
    svgLink: str | None
    campus: str
    corpus: str
    floor: int
    entrances: Entrances
    graph: Graph
    spaces: Spaces
