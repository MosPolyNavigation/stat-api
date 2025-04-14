from pydantic import BaseModel
from pydantic_core import core_schema
from typing import List, Tuple, Dict
from . import LocationData, PlanData, CorpusData, RoomData
import dataclasses
import sys

@dataclasses.dataclass
class DataEntry:
    Locations: List[LocationData]
    Corpuses: List[CorpusData]
    Plans: List[PlanData]
    Rooms: List[RoomData]


class VertexType(str):
    allowed_values = {"hallway","entrancesToAu","stair","crossing","crossingSpace","lift"}
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _a, _b
    ) -> core_schema.CoreSchema:
        def validate(value: str) -> VertexType:
            if value not in cls.allowed_values:
                raise ValueError(
                    f"Invalid value '{value}'. Allowed: {sorted(cls.allowed_values)}"
                )
            return cls(value)
        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.str_schema(),
        )


class Vertex(BaseModel):
    id: str
    x: int
    y: int
    type: VertexType
    neighborData: List[Tuple[str, int]]
    plan: PlanData


class Step:
    plan: PlanData
    way: List[Vertex]
    distance: int

    def __init__(self, plan: PlanData, first_vertex: Vertex):
        self.plan = plan
        self.way = [first_vertex]
        self.distance = 0


@dataclasses.dataclass
class ShortestWay:
    way: List[Vertex]
    distance: int


class Graph:
    location: LocationData
    plans: List[PlanData]
    corpuses: List[CorpusData]
    vertexex: List["Vertex"]

    def __init__(self, location: LocationData, plans: List[PlanData], corpuses: List[CorpusData]):
        self.location = location
        self.plans = plans
        self.corpuses = corpuses
        self.__fill_vertexes_by_raw_vertexes()
        self.__add_stairs()
        self.__add_crossings()

    def __fill_vertexes_by_raw_vertexes(self):
        plans_of_loc = [x for x in self.plans if x.corpus.location == self.location]
        vertexes = []
        for plan in plans_of_loc:
            for raw_vertex in plan.graph:
                vertexes.append(Vertex(
                    id=raw_vertex.id,
                    x=raw_vertex.x,
                    y=raw_vertex.y,
                    type=VertexType(raw_vertex.type),
                    neighborData=raw_vertex.neighborData,
                    plan=plan
                ))
            plan.graph = []
        self.vertexes = vertexes

    def __add_stairs(self):
        corpuses_of_loc = [x for x in self.corpuses if x.location == self.location]
        for corpus in corpuses_of_loc:
            for stairs_group in corpus.stairs:
                for stair_index in range(1, len(stairs_group)):
                    stair1_vertex = self.find_vertex_by_id(stairs_group[stair_index - 1])
                    stair2_vertex = self.find_vertex_by_id(stairs_group[stair_index])
                    self.__add_neighbor_both(stair1_vertex, stair2_vertex, 1085, 916)

    def find_vertex_by_id(self, id: str):
        return next((x for x in self.vertexes if x.id == id))

    @staticmethod
    def __add_neighbor_both(vertex1: Vertex, vertex2: Vertex, distance1to2: int, distance2to1: int):
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

    def get_shortest_way_from_to(self, id_vertex1: str, id_vertex2: str):
        def is_vertex_need_check(vertex: Vertex) -> bool:
            return (vertex.type == 'hallway' or
                    vertex.type == 'lift' or
                vertex.type == 'stair' or
                vertex.type == 'corpusTransition' or
                vertex.type == 'crossingSpace' or
                vertex.id == id_vertex1 or
                vertex.id == id_vertex2 or
                'crossing' in vertex.id
            )
        filtered_vertexes = [x for x in self.vertexes if is_vertex_need_check(x)]
        distances: Dict[str, int] = dict()
        ways: Dict[str, List[str]] = dict()
        for vertex in filtered_vertexes:
            distances[vertex.id] = sys.maxsize
            ways[vertex.id] = list()
        distances[id_vertex1] = 0
        finals = set()
        current_vertex_id = id_vertex1
        iterations = [0, 0]
        is_end_vertex_in_finals = False
        while len(finals) != len(filtered_vertexes) and not is_end_vertex_in_finals:
            iterations[0] += 1

            current_vertex_distance = distances.get(current_vertex_id)
            for neighbor_id, distance_to_neighbor in self.find_vertex_by_id(current_vertex_id).neighborData:
                if not self.find_vertex_by_id(neighbor_id) in filtered_vertexes:
                    continue
                iterations[1] += 1
                distance_between_current_and_neighbor = distance_to_neighbor
                neighbor_distance = distances.get(neighbor_id)

                if current_vertex_distance + distance_between_current_and_neighbor < neighbor_distance:
                    distances[neighbor_id] = current_vertex_distance + distance_between_current_and_neighbor
                    way_to_relaxing_vertex = ways.get(current_vertex_id)
                    way_to_relaxing_vertex.append(current_vertex_id)

            finals.add(current_vertex_id)
            if current_vertex_id == id_vertex2:
                is_end_vertex_in_finals = True
            min_distance = sys.maxsize
            next_vertex_id = ''
            for id, distance in distances.items():
                if distance < min_distance and not id in finals:
                    min_distance = distance
                    next_vertex_id = id
            if min_distance == sys.maxsize:
                break
            current_vertex_id = next_vertex_id
        for id, way in ways.items():
            way.append(id)
        return ShortestWay(way=[self.find_vertex_by_id(vertex_id) for vertex_id in ways.get(id_vertex2)], distance=distances.get(id_vertex2))

    @staticmethod
    def get_distance_between2_vertexes(vertex1: Vertex, vertex2_id: str) -> int:
        return next((note for note in vertex1.neighborData if note[0] == vertex2_id))[1]


class Route:
    steps: List["Step"]
    to: str
    from_: str
    activeStep: int
    fullDistance: int
    graph: Graph

    def __init__(self, from_: str, to: str, graph: Graph):
        self.from_ = from_
        self.to = to
        self.graph = graph
        self.__build_way_and_get_steps()

    def __build_way_and_get_steps(self):
        graph = self.graph
        way_and_distance = graph.get_shortest_way_from_to(self.from_, self.to)
        self.fullDistance = way_and_distance.distance

        way = [x for x in way_and_distance.way]
        first_vertex = way.pop(0)
        self.steps = [Step(plan=first_vertex.plan, first_vertex=first_vertex)]
        for way_vertex in way:
            last_step = self.steps[-1]
            if way_vertex.plan == last_step.plan:
                last_step.distance += graph.get_distance_between2_vertexes(
                    last_step.way[-1],
                    way_vertex.id
                )
                last_step.way.append(way_vertex)
            else:
                self.steps.append(Step(way_vertex.plan, way_vertex))
        first_step = self.steps[0]
        if len(first_step.way) == 1:
            first_step.way.insert(0, graph.find_vertex_by_id(first_step.way[0].neighborData[0][0]))
            first_step.distance = first_step.way[0].neighborData[0][1]
        last_step = self.steps[-1]
        if last_step and len(last_step.way) == 1:
            last_step.way.append(graph.find_vertex_by_id(last_step.way[0].neighborData[0][0]))
            last_step.distance = last_step.way[0].neighborData[0][1]
        self.steps = [x for x in self.steps if len(x.way) > 1]
