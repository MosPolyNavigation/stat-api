import asyncio
import csv
import json
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.nav.location import Location as LocationModel
from app.models.nav.corpus import Corpus as CorpusModel
from app.models.nav.plan import Plan as PlanModel
from app.models.nav.types import Type as TypeModel
from app.models.nav.auditory import Auditory as AuditoryModel


class Plan(BaseModel):
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


def load_plans_from_csv():
    data: list[Plan] = []
    with open('nav_data/plans.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            plan = Plan(
                id=row[0],
                corpusId=row[1],
                floor=int(row[2]),
                available=row[3] == 'TRUE',
                entrances=json.dumps(json.loads(row[4]), separators=(',', ':')),
                graph=json.dumps(json.loads(row[5]), separators=(',', ':')),
                wayToSvg=row[6],
                nearest_entrance=row[7] if len(row[7]) != 0 else None,
                nearest_wc_man=row[8] if len(row[8]) != 0 else None,
                nearest_wc_woman=row[9] if len(row[9]) != 0 else None,
                nearest_wc=row[10] if len(row[10]) != 0 else None,
            )
            data.append(plan)
    return data


class Auditory(BaseModel):
    id: str
    plan_id: str
    type: str
    available: bool
    name: str
    sign_str: str | None
    additional_info: str | None
    comments: str | None
    link: str | None


def load_auditories_from_csv():
    data: list[Auditory] = []
    with open('nav_data/auds.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            aud = Auditory(
                plan_id=row[0],
                id=row[1],
                type=row[2],
                available=row[3] == 'TRUE',
                name=row[4],
                sign_str=row[5] if len(row[5]) != 0 else None,
                additional_info=row[6] if len(row[6]) != 0 else None,
                comments=row[7] if len(row[7]) != 0 else None,
                link=row[8] if len(row[8]) != 0 else None
            )
            data.append(aud)
    return data


class Location(BaseModel):
    id: str
    name: str
    short_name: str
    available: bool
    address: str
    metro: str
    crossings: str
    comments: str | None


def load_locations_from_csv():
    data: list[Location] = []
    with open('nav_data/locations.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            loc = Location(
                id=row[0],
                name=row[1],
                short_name=row[2],
                available=row[3] == 'TRUE',
                address=row[4],
                metro=row[5],
                crossings=json.dumps(json.loads(row[6]), separators=(',', ':')),
                comments=row[7] if len(row[7]) != 0 else None
            )
            data.append(loc)
    return data


class Corpus(BaseModel):
    id: str
    loc_id: str
    name: str
    available: bool
    ladders: str
    comments: str | None


def load_corpuses_from_csv():
    data: list[Corpus] = []
    with open('nav_data/corpuses.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            corpus = Corpus(
                id=row[0],
                loc_id=row[1],
                name=row[2],
                available=row[3] == 'TRUE',
                ladders=json.dumps(json.loads(row[4]), separators=(',', ':')),
                comments=row[5] if len(row[5]) != 0 else None
            )
            data.append(corpus)
    return data


def get_types(auds: list[Auditory]) -> list[str]:
    types_ = set()
    for aud in auds:
        types_.add(aud.type)
    return list(types_)


type StrIntId = dict[str, int]


async def fill_locations(db: AsyncSession, locations: list[Location]) -> StrIntId:
    ids: StrIntId = dict()
    locations_db: list[LocationModel] = []
    for i, loc in enumerate(locations):
        ids[loc.id] = i + 1
        location = LocationModel(
            id=i+1,
            id_sys=loc.id,
            name=loc.name,
            short=loc.short_name,
            ready=loc.available,
            address=loc.address,
            metro=loc.metro,
            crossings=loc.crossings,
            comments=loc.comments
        )
        locations_db.append(location)
    db.add_all(locations_db)
    await db.commit()
    return ids


async def fill_corpuses(db: AsyncSession, corpuses: list[Corpus], loc_ids: StrIntId) -> StrIntId:
    ids: StrIntId = dict()
    corpuses_db: list[CorpusModel] = []
    for i, cor in enumerate(corpuses):
        ids[cor.id] = i + 1
        corpus = CorpusModel(
            id=i + 1,
            id_sys=cor.id,
            loc_id=loc_ids[cor.loc_id],
            name=cor.name,
            ready=cor.available,
            stair_groups=cor.ladders,
            comments=cor.comments
        )
        corpuses_db.append(corpus)
    db.add_all(corpuses_db)
    await db.commit()
    return ids


async def fill_plans(db: AsyncSession, plans: list[Plan], cor_ids: StrIntId) -> StrIntId:
    ids: StrIntId = dict()
    plans_db: list[PlanModel] = []
    for i, pl in enumerate(plans):
        ids[pl.id] = i + 1
        plan = PlanModel(
            id=i + 1,
            id_sys=pl.id,
            cor_id=cor_ids[pl.corpusId],
            floor_id=pl.floor+2,
            ready=pl.available,
            entrances=pl.entrances,
            graph=pl.graph,
            svg_id=None,
            nearest_entrance=pl.nearest_entrance,
            nearest_man_wc=pl.nearest_wc_man,
            nearest_woman_wc=pl.nearest_wc_woman,
            nearest_shared_wc=pl.nearest_wc
        )
        plans_db.append(plan)
    db.add_all(plans_db)
    await db.commit()
    return ids


async def fill_types(db: AsyncSession, types_: list[str]) -> StrIntId:
    ids: StrIntId = dict()
    types_db: list[TypeModel] = []
    for i, type_ in enumerate(types_):
        ids[type_] = i + 1
        type_db = TypeModel(
            id=i + 1,
            name=type_
        )
        types_db.append(type_db)
    db.add_all(types_db)
    await db.commit()
    return ids


async def fill_auds(db: AsyncSession, auds: list[Auditory], pl_ids: StrIntId, type_ids: StrIntId):
    auds_db: list[AuditoryModel] = []
    for i, aud in enumerate(auds):
        aud_db = AuditoryModel(
            id=i + 1,
            id_sys=aud.id,
            type_id=type_ids[aud.type],
            ready=aud.available,
            plan_id=pl_ids[aud.plan_id],
            name=aud.name,
            text_from_sign=aud.sign_str,
            additional_info=aud.additional_info,
            comments=aud.comments,
            link=aud.link
        )
        auds_db.append(aud_db)
    db.add_all(auds_db)
    await db.commit()


async def main():
    locations = load_locations_from_csv()
    corpuses = load_corpuses_from_csv()
    plans = load_plans_from_csv()
    auds = load_auditories_from_csv()
    types_ = get_types(auds)
    async with AsyncSessionLocal() as db:
        loc_ids: StrIntId = await fill_locations(db, locations)
        cor_ids: StrIntId = await fill_corpuses(db, corpuses, loc_ids)
        pl_ids: StrIntId = await fill_plans(db, plans, cor_ids)
        type_ids: StrIntId = await fill_types(db, types_)
        await fill_auds(db, auds, pl_ids, type_ids)


if __name__ == '__main__':
    asyncio.run(main())
