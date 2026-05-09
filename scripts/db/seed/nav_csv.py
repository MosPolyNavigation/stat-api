import asyncio
import csv
import json
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import load_settings, Settings
from app.database import init_database, close_database, get_session_maker
from app.models.nav.location import Location as LocationModel
from app.models.nav.corpus import Corpus as CorpusModel
from app.models.nav.plan import Plan as PlanModel
from app.models.nav.types import Type as TypeModel
from app.models.nav.auditory import Auditory as AuditoryModel

StrIntId = dict[str, int]


# ── Pydantic-модели для парсинга CSV ─────────────────────────────────────
class PlanCSV(BaseModel):
    id: str
    corpusId: str
    floor: int
    available: bool
    entrances: str
    graph: str
    wayToSvg: str
    nearest_entrance: str | None
    nearest_wc_man: str | None
    nearest_wc_woman: str | None
    nearest_wc: str | None


class AuditoryCSV(BaseModel):
    id: str
    plan_id: str
    type: str
    available: bool
    name: str
    sign_str: str | None
    additional_info: str | None
    comments: str | None
    link: str | None


class LocationCSV(BaseModel):
    id: str
    name: str
    short_name: str
    available: bool
    address: str
    metro: str
    crossings: str
    comments: str | None


class CorpusCSV(BaseModel):
    id: str
    loc_id: str
    name: str
    available: bool
    ladders: str
    comments: str | None


# ── Загрузчики из CSV ───────────────────────────────────────────────────
def _load_plans(path: Path) -> list[PlanCSV]:
    data: list[PlanCSV] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            data.append(PlanCSV(
                id=row[0],
                corpusId=row[1],
                floor=int(row[2]),
                available=row[3] == "TRUE",
                entrances=json.dumps(json.loads(row[4]), separators=(",", ":")),
                graph=json.dumps(json.loads(row[5]), separators=(",", ":")),
                wayToSvg=row[6],
                nearest_entrance=row[7] if len(row[7]) else None,
                nearest_wc_man=row[8] if len(row[8]) else None,
                nearest_wc_woman=row[9] if len(row[9]) else None,
                nearest_wc=row[10] if len(row[10]) else None,
            ))
    return data


def _load_auditories(path: Path) -> list[AuditoryCSV]:
    data: list[AuditoryCSV] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            data.append(AuditoryCSV(
                plan_id=row[0],
                id=row[1],
                type=row[2],
                available=row[3] == "TRUE",
                name=row[4],
                sign_str=row[5] if len(row[5]) else None,
                additional_info=row[6] if len(row[6]) else None,
                comments=row[7] if len(row[7]) else None,
                link=row[8] if len(row[8]) else None,
            ))
    return data


def _load_locations(path: Path) -> list[LocationCSV]:
    data: list[LocationCSV] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            data.append(LocationCSV(
                id=row[0],
                name=row[1],
                short_name=row[2],
                available=row[3] == "TRUE",
                address=row[4],
                metro=row[5],
                crossings=json.dumps(json.loads(row[6]), separators=(",", ":")),
                comments=row[7] if len(row[7]) else None,
            ))
    return data


def _load_corpuses(path: Path) -> list[CorpusCSV]:
    data: list[CorpusCSV] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            data.append(CorpusCSV(
                id=row[0],
                loc_id=row[1],
                name=row[2],
                available=row[3] == "TRUE",
                ladders=json.dumps(json.loads(row[4]), separators=(",", ":")),
                comments=row[5] if len(row[5]) else None,
            ))
    return data


def _get_unique_types(auds: list[AuditoryCSV]) -> list[str]:
    return list({aud.type for aud in auds})


# ── Функции заполнения БД ────────────────────────────────────────────────
async def _clear_tables(db: AsyncSession) -> None:
    """Очищает таблицы в порядке, безопасном для внешних ключей."""
    await db.execute(delete(AuditoryModel))
    await db.execute(delete(TypeModel))
    await db.execute(delete(PlanModel))
    await db.execute(delete(CorpusModel))
    await db.execute(delete(LocationModel))
    await db.commit()


async def _fill_locations(db: AsyncSession, locations: list[LocationCSV]) -> StrIntId:
    ids: StrIntId = {}
    objs = [
        LocationModel(
            id=i + 1,
            id_sys=loc.id,
            name=loc.name,
            short=loc.short_name,
            ready=loc.available,
            address=loc.address,
            metro=loc.metro,
            crossings=loc.crossings,
            comments=loc.comments,
        )
        for i, loc in enumerate(locations)
    ]
    for i, loc in enumerate(locations):
        ids[loc.id] = i + 1
    db.add_all(objs)
    await db.commit()
    return ids


async def _fill_corpuses(db: AsyncSession, corpuses: list[CorpusCSV], loc_ids: StrIntId) -> StrIntId:
    ids: StrIntId = {}
    objs = [
        CorpusModel(
            id=i + 1,
            id_sys=cor.id,
            loc_id=loc_ids[cor.loc_id],
            name=cor.name,
            ready=cor.available,
            stair_groups=cor.ladders,
            comments=cor.comments,
        )
        for i, cor in enumerate(corpuses)
    ]
    for i, cor in enumerate(corpuses):
        ids[cor.id] = i + 1
    db.add_all(objs)
    await db.commit()
    return ids


async def _fill_plans(db: AsyncSession, plans: list[PlanCSV], cor_ids: StrIntId) -> StrIntId:
    ids: StrIntId = {}
    objs = [
        PlanModel(
            id=i + 1,
            id_sys=pl.id,
            cor_id=cor_ids[pl.corpusId],
            floor_id=pl.floor + 2,
            ready=pl.available,
            entrances=pl.entrances,
            graph=pl.graph,
            svg_id=None,
            nearest_entrance=pl.nearest_entrance,
            nearest_man_wc=pl.nearest_wc_man,
            nearest_woman_wc=pl.nearest_wc_woman,
            nearest_shared_wc=pl.nearest_wc,
        )
        for i, pl in enumerate(plans)
    ]
    for i, pl in enumerate(plans):
        ids[pl.id] = i + 1
    db.add_all(objs)
    await db.commit()
    return ids


async def _fill_types(db: AsyncSession, types_: list[str]) -> StrIntId:
    ids: StrIntId = {}
    objs = [TypeModel(id=i + 1, name=t) for i, t in enumerate(types_)]
    for i, t in enumerate(types_):
        ids[t] = i + 1
    db.add_all(objs)
    await db.commit()
    return ids


async def _fill_auditories(
    db: AsyncSession,
    auds: list[AuditoryCSV],
    pl_ids: StrIntId,
    type_ids: StrIntId,
) -> None:
    objs = [
        AuditoryModel(
            id=i + 1,
            id_sys=aud.id,
            type_id=type_ids[aud.type],
            ready=aud.available,
            plan_id=pl_ids[aud.plan_id],
            name=aud.name,
            text_from_sign=aud.sign_str,
            additional_info=aud.additional_info,
            comments=aud.comments,
            link=aud.link,
        )
        for i, aud in enumerate(auds)
    ]
    db.add_all(objs)
    await db.commit()


async def _run_migration(
    nav_dir: Path,
    settings: Settings,
    clean: bool,
    dry_run: bool,
) -> None:
    """Внутренняя логика: загрузка CSV → заполнение БД."""
    # Загрузка данных
    locations = _load_locations(nav_dir / "locations.csv")
    corpuses = _load_corpuses(nav_dir / "corpuses.csv")
    plans = _load_plans(nav_dir / "plans.csv")
    auds = _load_auditories(nav_dir / "auds.csv")
    types_ = _get_unique_types(auds)

    typer.echo(f"📦 Загружено: {len(locations)} locations, {len(corpuses)} corpuses, "
               f"{len(plans)} plans, {len(auds)} auditories, {len(types_)} types")

    if dry_run:
        typer.echo("✅ [DRY RUN] Данные готовы к загрузке")
        return

    # Инициализация БД
    init_database(settings)
    session_maker = get_session_maker()

    try:
        async with session_maker() as db:
            if clean:
                typer.echo("🧹 Очистка таблиц...")
                await _clear_tables(db)

            typer.echo("🌱 Заполнение БД...")
            loc_ids = await _fill_locations(db, locations)
            cor_ids = await _fill_corpuses(db, corpuses, loc_ids)
            pl_ids = await _fill_plans(db, plans, cor_ids)
            type_ids = await _fill_types(db, types_)
            await _fill_auditories(db, auds, pl_ids, type_ids)

        typer.echo("✅ Навигационные данные загружены успешно")
    finally:
        await close_database()


# ── Typer-команда (без декоратора — чистая бизнес-логика) ───────────────
def nav_csv_command(
    nav_dir: Annotated[
        Path,
        typer.Argument(help="Папка с CSV-файлами навигации (locations.csv, corpuses.csv, plans.csv, auds.csv)")
    ] = Path("nav_data"),
    clean: Annotated[
        bool,
        typer.Option("--clean", help="Очистить таблицы перед загрузкой"),
    ] = True,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Показать план без выполнения"),
    ] = False,
) -> None:
    """
    Заполнение БД навигационными данными из CSV.
    Строка подключения берётся из конфига (переменная STATAPI_CONFIG).
    """
    # Валидация путей к файлам
    required_files = ["locations.csv", "corpuses.csv", "plans.csv", "auds.csv"]
    for fname in required_files:
        fpath = nav_dir / fname
        if not fpath.exists():
            typer.echo(f"❌ Файл не найден: {fpath}")
            raise typer.Exit(1)

    # Валидация DSN через конфиг
    settings = load_settings()

    typer.echo(f"📂 Папка навигации: {nav_dir.resolve()}")
    typer.echo(f"🧹 Очистка: {clean}, Dry run: {dry_run}")

    try:
        asyncio.run(_run_migration(nav_dir, settings, clean=clean, dry_run=dry_run))
    except Exception as e:
        typer.echo(f"💥 Ошибка: {e}")
        raise typer.Exit(1)
