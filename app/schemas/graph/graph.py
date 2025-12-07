from itertools import pairwise
from pydantic import BaseModel
from typing import List, Tuple, Dict
from pydantic_core import core_schema
from app.schemas import LocationData, PlanData, CorpusData
import dataclasses
import math
import time
import heapq


@dataclasses.dataclass
class DataEntry:
    Locations: List[LocationData]
    Corpuses: List[CorpusData]
    Plans: List[PlanData]


class VertexType(str):
    allowed_values = {
        "hallway",
        "entrancesToAu",
        "stair",
        "crossing",
        "crossingSpace",
        "lift"
    }

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _a, _b
    ) -> core_schema.CoreSchema:
        def validate(value: str) -> VertexType:
            if value not in cls.allowed_values:
                raise ValueError(
                    f"Invalid value '{value}'. Allowed: \
{sorted(cls.allowed_values)}"
                )
            return cls(value)
        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.str_schema(),
        )


class Vertex(BaseModel):
    id: str
    x: float
    y: float
    type: VertexType
    neighborData: List[Tuple[str, float]]
    plan: PlanData

    def __hash__(self):
        return hash((self.id, self.x, self.y, self.type))


class VertexOut(BaseModel):
    id: str
    x: float
    y: float
    type: VertexType
    neighborData: List[Tuple[str, float]]


@dataclasses.dataclass
class ShortestWay:
    way: List[Vertex]
    distance: int


class ShortestWayOut(BaseModel):
    way: List[VertexOut]
    distance: int


class Graph:
    location: LocationData
    plans: List[PlanData]
    corpuses: List[CorpusData]
    vertexes: Dict[str, "Vertex"]

    def __init__(
        self,
        location: LocationData,
        plans: List[PlanData],
        corpuses: List[CorpusData]
    ):
        self.location = location
        self.plans = plans
        self.corpuses = corpuses
        self.__fill_vertexes_by_raw_vertexes()
        self.__add_stairs()
        self.__add_crossings()

    def __fill_vertexes_by_raw_vertexes(self):
        plans_of_loc = [
            plan for plan in self.plans
            if plan.corpus.location == self.location
        ]
        vertexes = dict()
        for plan in plans_of_loc:
            for raw_vertex in plan.graph:
                vertexes[raw_vertex.id] = Vertex(
                    id=raw_vertex.id,
                    x=raw_vertex.x,
                    y=raw_vertex.y,
                    type=VertexType(raw_vertex.type),
                    neighborData=raw_vertex.neighborData,
                    plan=plan
                )
        self.vertexes = vertexes

    def __add_stairs(self):
        corpuses_of_loc = [
            x for x in self.corpuses if x.location == self.location
        ]
        for corpus in corpuses_of_loc:
            for stairs_group in corpus.stairs:
                for stair_id1, stair_id2 in pairwise(stairs_group):
                    stair1_vertex = self.find_vertex_by_id(stair_id1)
                    stair2_vertex = self.find_vertex_by_id(stair_id2)
                    self.__add_neighbor_both(
                        stair1_vertex, stair2_vertex,
                        1085, 916
                    )

    def find_vertex_by_id(self, id_: str) -> Vertex:
        return self.vertexes[id_]

    @staticmethod
    def __add_neighbor_both(
        vertex1: Vertex,
        vertex2: Vertex,
        distance1to2: int,
        distance2to1: int
    ):
        vertex1.neighborData.append((vertex2.id, distance1to2))
        vertex2.neighborData.append((vertex1.id, distance2to1))

    def __add_crossings(self):
        for crossing_group in self.location.crossings:
            crossing1_id, crossing2_id, distance = crossing_group
            self.__add_neighbor_both(
                self.find_vertex_by_id(crossing1_id),
                self.find_vertex_by_id(crossing2_id),
                distance,
                distance
            )

    def get_shortest_way_from_to(
        self,
        start: str,
        end: str
    ) -> ShortestWay:
        st_time = time.time()
        allowed_types = {
            'hallway',
            'lift',
            'stair',
            'corpusTransition',
            'crossingSpace'
        }

        # Фильтрация вершин через словарь
        valid_ids = {k for k, v in self.vertexes.items()
                     if v.type in allowed_types
                     or k in {start, end}
                     or 'crossing' in k}

        distances = {vid: math.inf for vid in valid_ids}
        previous: Dict[str, str | None] = {vid: None for vid in valid_ids}
        distances[start] = 0

        heap = [(0, start)]
        visited = set()

        while heap:
            curr_dist, current_id = heapq.heappop(heap)

            if current_id == end:
                break

            if current_id in visited:
                continue

            visited.add(current_id)

            current = self.vertexes[current_id]
            for neighbor, dist in current.neighborData:
                if neighbor not in valid_ids:
                    continue

                new_dist = curr_dist + dist
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_id
                    heapq.heappush(heap, (math.floor(new_dist), neighbor))

        # Восстановление пути
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous.get(current)
        end_time = time.time()
        e_time = end_time - st_time
        print(f"The task took {e_time:.4f} seconds to complete.")
        return ShortestWay(
            way=[self.vertexes[vid] for vid in reversed(path) if vid],
            distance=math.floor(distances.get(end, math.inf))
        )

    @staticmethod
    def get_distance_between2_vertexes(
        vertex1: Vertex, vertex2_id: str
    ) -> float:
        return next(
            note for note in vertex1.neighborData if note[0] == vertex2_id
        )[1]
