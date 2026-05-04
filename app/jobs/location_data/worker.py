import json
import logging
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session_maker
from app.jobs.manager import scheduled_task
from app.jobs.schedule.get_graph import parse_corpus, parse_location, parse_plan
from app.models.nav.auditory import Auditory
from app.models.nav.corpus import Corpus
from app.models.nav.location import Location
from app.models.nav.plan import Plan
from app.schemas import DataDto, Graph
from app.schemas.graph.graph import DataEntry
from app.state import AppState

logger = logging.getLogger(f"uvicorn.{__name__}")


def safe_json_loads(raw: str | None, default):
    """Парсинг JSON-строки из БД. При ошибке возвращается default."""
    if not raw:
        return default
    try:
        return json.loads(raw)
    except ValueError:
        return default


async def build_location_data_json(db: AsyncSession) -> Dict[str, Any]:
    """Сбор структуры locationData."""
    locs = (await db.execute(select(Location).where(Location.ready.is_(True)))).scalars().all()

    locations_json: List[Dict[str, Any]] = []
    for loc in locs:
        locations_json.append(
            {
                "id": loc.id_sys,
                "title": loc.name,
                "short": loc.short,
                "available": bool(loc.ready),
                "address": loc.address,
                "crossings": safe_json_loads(loc.crossings, None),
            }
        )

    corpuses = (
        await db.execute(
            select(Corpus)
            .options(selectinload(Corpus.locations))
            .where(Corpus.ready.is_(True))
        )
    ).scalars().all()

    corpuses_json: List[Dict[str, Any]] = []
    for corpus in corpuses:
        corpuses_json.append(
            {
                "id": corpus.id_sys,
                "locationId": corpus.locations.id_sys,
                "title": corpus.name,
                "available": bool(corpus.ready),
                "stairs": safe_json_loads(corpus.stair_groups, None),
            }
        )

    plans = (
        await db.execute(
            select(Plan)
            .options(
                selectinload(Plan.corpus).selectinload(Corpus.locations),
                selectinload(Plan.floor),
                selectinload(Plan.svg),
            )
            .where(Plan.ready.is_(True))
        )
    ).scalars().all()

    plans_json: List[Dict[str, Any]] = []
    for plan in plans:
        plans_json.append(
            {
                "id": plan.id_sys,
                "corpusId": plan.corpus.id_sys,
                "floor": str(plan.floor.name),
                "available": bool(plan.ready),
                "wayToSvg": plan.svg.link if plan.svg is not None else "",
                "graph": safe_json_loads(plan.graph, []),
                "entrances": safe_json_loads(plan.entrances, []),
                "nearest": {
                    "enter": plan.nearest_entrance or "",
                    "wm": plan.nearest_man_wc,
                    "ww": plan.nearest_woman_wc,
                    "ws": plan.nearest_shared_wc,
                },
            }
        )

    rooms = (
        await db.execute(
            select(Auditory)
            .options(selectinload(Auditory.typ), selectinload(Auditory.plans))
            .where(Auditory.ready.is_(True))
        )
    ).scalars().all()

    rooms_json: List[Dict[str, Any]] = []
    for room in rooms:
        rooms_json.append(
            {
                "id": room.id_sys,
                "planId": room.plans.id_sys,
                "type": room.typ.name,
                "available": bool(room.ready),
                "numberOrTitle": room.name or "",
                "tabletText": room.text_from_sign or "",
                "addInfo": room.additional_info or "",
            }
        )

    return {
        "locations": locations_json,
        "corpuses": corpuses_json,
        "plans": plans_json,
        "rooms": rooms_json,
    }


def build_data_entry(dto: DataDto) -> DataEntry:
    """Преобразование DataDto в DataEntry (структура, из которой строится граф)."""
    locations = list(map(parse_location, dto.locations))
    corpuses = [parse_corpus(x, locations) for x in dto.corpuses]
    plans = [parse_plan(x, corpuses) for x in dto.plans]
    return DataEntry(Locations=locations, Corpuses=corpuses, Plans=plans)


@scheduled_task(name="fetch_location_data")
async def fetch_location_data(state: AppState):
    """Воркер: собирает locationData JSON и пересобирает графы навигации в state."""
    if state._location_lock.locked():
        return

    async with state._location_lock:
        try:
            logger.info("Starting locationData fetching")

            session_maker = get_session_maker()
            async with session_maker() as db:
                raw_json = await build_location_data_json(db)

            dto = DataDto(**raw_json)
            state.location_data_json = dto.model_dump(mode="json", exclude_none=True)

            data_entry = build_data_entry(dto)
            new_graphs: Dict[str, Graph] = {}
            for loc_id in map(lambda loc: loc.id, data_entry.Locations):
                location = next((x for x in data_entry.Locations if x.id == loc_id))
                new_graphs[loc_id] = Graph(location, data_entry.Plans, data_entry.Corpuses)
            state.global_graph = new_graphs

            logger.info("locationData fetching finished successful")
        except Exception:
            logger.exception("locationData fetching failed with error")
