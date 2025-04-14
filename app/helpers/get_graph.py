from app.schemas import DataDto, PlanData, LocationData, CorpusData, RoomData, LocationDto, CorpusDto, PlanDto, \
    Graph, DataEntry
from typing import List
from .parser import fill_room_data
import httpx

dataUrl = 'https://mospolynavigation.github.io/polyna-preprocess/locationsV2.json'


def parse_location(location: LocationDto) -> LocationData:
    return LocationData(
        id=location.id,
        title=location.title,
        short=location.short,
        address=location.address,
        available=location.available,
        crossings=location.crossings or []
    )


def parse_corpus(corpus: CorpusDto, locations: List[LocationData]) -> CorpusData:
    return CorpusData(
        id=corpus.id,
        title=corpus.title,
        location=next((v for v in locations if v.id == corpus.locationId)),
        available=corpus.available,
        stairs=corpus.stairs or []
    )


def parse_plan(plan: PlanDto, corpuses: List[CorpusData]) -> PlanData:
    return PlanData(
        id=plan.id,
        corpus=next((v for v in corpuses if v.id == plan.corpusId)),
        available=plan.available,
        wayToSvg=plan.wayToSvg,
        graph=plan.graph,
        floor=int(plan.floor),
        entrances=plan.entrances
    )


async def fetch_data(url) -> DataDto:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
    return DataDto(**r.json())


async def parse_data() -> DataEntry:
    data = await fetch_data(dataUrl)
    locations: List[LocationData] = list(map(parse_location, data.locations))
    corpuses: List[CorpusData] = [parse_corpus(x, locations) for x in data.corpuses]
    plans: List[PlanData] = [parse_plan(x, corpuses) for x in data.plans]
    rooms: List[RoomData] = [lv for lv in [fill_room_data(
        x, next((v for v in plans if v.id == x.planId))
    ) for x in data.rooms] if lv is not None]
    return DataEntry(
        Locations=locations, Corpuses=corpuses, Plans=plans, Rooms=rooms
    )

async def get_graph(data: DataEntry, loc_id: str):
    locations, corpuses, plans = data.Locations, data.Corpuses, data.Plans
    location_bs = next((x for x in locations if x.id == loc_id))
    graph_bs = Graph(location_bs, plans, corpuses)
    return graph_bs
