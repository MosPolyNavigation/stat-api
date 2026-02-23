import json
import logging
from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.nav.auditory import Auditory
from app.models.nav.corpus import Corpus

from app.models.nav.location import Location
from app.models.nav.plan import Plan

from app.schemas import DataDto
from app.schemas.graph.graph import DataEntry
from app.schemas import Graph


from app.jobs.schedule.get_graph import parse_location, parse_corpus, parse_plan
import app.globals as globals_

logger = logging.getLogger(f"uvicorn.{__name__}")


def safe_json_loads(raw: str | None, default):
    """ Парсинг JSON-строки из БД. При ошибке  возвращается default """
    if not raw:
        return default
    try:
        return json.loads(raw)
    except ValueError:
        return default


async def build_location_data_json(db: AsyncSession) -> Dict[str, Any]:
    """Сбор структуры locationData """
    locs = (await db.execute(select(Location).where(Location.ready.is_(True)))).scalars().all()

    locations_json: List[Dict[str, Any]] = []
    # Локации
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

    # Корпуса
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

    # планы
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

    # Комнаты (auditories)
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
    """Преобразование DataDto в DataEntry (структура, из которой строится граф)"""
    locations = list(map(parse_location, dto.locations))
    corpuses = [parse_corpus(x, locations) for x in dto.corpuses]
    plans = [parse_plan(x, corpuses) for x in dto.plans]
    return DataEntry(Locations=locations, Corpuses=corpuses, Plans=plans)

# Воркер
async def fetch_location_data():
    """ Воркер. собирает json и обновляет графы в памяти """

    # Защита от параллельного запуска
    if globals_.location_data_locker:
        return

    globals_.location_data_locker = True
    try:
        logger.info("Starting locationData fetching")

        # Собраем JSON из БД
        async with AsyncSessionLocal() as db:
            raw_json = await build_location_data_json(db)
        # Привеодим к нужной схеме
        dto = DataDto(**raw_json)

        # Сначала сохраняем JSOn в память
        globals_.location_data_json = dto.model_dump(mode="json", exclude_none=True)

        # Строим графы
        data_entry = build_data_entry(dto)
        new_graphs: Dict[str, Graph] = {}
        for loc_id in map(lambda loc: loc.id, data_entry.Locations):
            location = next((x for x in data_entry.Locations if x.id == loc_id))
            new_graphs[loc_id] = Graph(location, data_entry.Plans, data_entry.Corpuses)

        #Сохраняем граф
        globals_.global_graph = new_graphs

        logger.info("locationData fetching finished successful")
    except Exception:
        logger.exception("locationData fetching failed with error")
    finally:
        globals_.location_data_locker = False