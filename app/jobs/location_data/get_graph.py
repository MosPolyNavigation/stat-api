from app.schemas.graph.dto import LocationDto, CorpusDto, PlanDto
from app.schemas import PlanData, LocationData, CorpusData
from typing import List


def parse_location(location: LocationDto) -> LocationData:
    return LocationData(
        id=location.id,
        title=location.title,
        short=location.short,
        address=location.address,
        available=location.available,
        crossings=location.crossings or [],
    )


def parse_corpus(corpus: CorpusDto, locations: List[LocationData]) -> CorpusData:
    return CorpusData(
        id=corpus.id,
        title=corpus.title,
        location=next((v for v in locations if v.id == corpus.locationId)),
        available=corpus.available,
        stairs=corpus.stairs or [],
    )


def parse_plan(plan: PlanDto, corpuses: List[CorpusData]) -> PlanData:
    return PlanData(
        id=plan.id,
        corpus=next((v for v in corpuses if v.id == plan.corpusId)),
        available=plan.available,
        wayToSvg=plan.wayToSvg,
        graph=plan.graph or [],
        floor=int(plan.floor),
        entrances=plan.entrances or [],
    )
