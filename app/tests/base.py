import asyncio
import os
from datetime import datetime
from pwdlib import PasswordHash
from app.config import get_settings
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from pathlib import Path
from pydantic import RootModel

path = get_settings().sqlalchemy_database_url.path.removeprefix("/")
try:
    os.remove(path)
except FileNotFoundError:
    pass

from app.tests.app import app
from app.models import Base
from app.database import engine, AsyncSessionLocal
from app.helpers.data import goals, roles, rights, roles_rights_goals, review_status
from app import models
from app.schemas.rasp.schedule import Auditory
import app.globals as globals_

add_pagination(app)


class Schedule(RootModel[dict[str, Auditory]]):
    pass


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal.begin() as db:
        client = models.ClientId(
            id=1,
            ident="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            creation_date=datetime(2025, 1, 1, 8, 0, 0),
        )
        client_2 = models.ClientId(
            id=2,
            ident="22e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            creation_date=datetime(2025, 1, 2, 8, 0, 0),
        )
        db.add_all([client, client_2])
        review_statuses: list[models.ReviewStatus] = list([
            models.ReviewStatus(id=id_, name=name) for id_, name in review_status.items()
        ])
        db.add_all(review_statuses)

        db.add_all([
            models.ValueType(id=1, name="int", description="Integer value"),
            models.ValueType(id=2, name="string", description="String value"),
            models.ValueType(id=3, name="bool", description="Boolean value"),
        ])
        db.add_all([
            models.EventType(id=1, code_name="site", description="Site events"),
            models.EventType(id=2, code_name="auds", description="Auditory selection events"),
            models.EventType(id=3, code_name="ways", description="Route build events"),
            models.EventType(id=4, code_name="plans", description="Plan change events"),
        ])
        db.add_all([
            models.PayloadType(id=1, code_name="endpoint", description="Visited site endpoint", value_type_id=2),
            models.PayloadType(id=2, code_name="auditory_id", description="Selected auditory identifier", value_type_id=2),
            models.PayloadType(id=3, code_name="start_id", description="Route start identifier", value_type_id=2),
            models.PayloadType(id=4, code_name="end_id", description="Route destination identifier", value_type_id=2),
            models.PayloadType(id=5, code_name="success", description="Operation success flag", value_type_id=3),
            models.PayloadType(id=6, code_name="plan_id", description="Selected plan identifier", value_type_id=2),
        ])
        db.add_all([
            models.AllowedPayload(event_type_id=1, payload_type_id=1),
            models.AllowedPayload(event_type_id=2, payload_type_id=2),
            models.AllowedPayload(event_type_id=2, payload_type_id=5),
            models.AllowedPayload(event_type_id=3, payload_type_id=3),
            models.AllowedPayload(event_type_id=3, payload_type_id=4),
            models.AllowedPayload(event_type_id=3, payload_type_id=5),
            models.AllowedPayload(event_type_id=4, payload_type_id=6),
        ])

        site_event = models.Event(
            id=1,
            client=client,
            event_type_id=1,
            trigger_time=datetime(2025, 1, 1, 10, 0, 0),
        )
        aud_event = models.Event(
            id=2,
            client=client,
            event_type_id=2,
            trigger_time=datetime(2025, 1, 1, 11, 0, 0),
        )
        way_event = models.Event(
            id=3,
            client=client,
            event_type_id=3,
            trigger_time=datetime(2025, 1, 1, 12, 0, 0),
        )
        plan_event = models.Event(
            id=4,
            client=client_2,
            event_type_id=4,
            trigger_time=datetime(2025, 1, 2, 9, 0, 0),
        )
        db.add_all([site_event, aud_event, way_event, plan_event])
        db.add_all([
            models.Payload(id=1, event=site_event, type_id=1, value="site"),
            models.Payload(id=2, event=aud_event, type_id=2, value="a-100"),
            models.Payload(id=3, event=aud_event, type_id=5, value="true"),
            models.Payload(id=4, event=way_event, type_id=3, value="a-100"),
            models.Payload(id=5, event=way_event, type_id=4, value="a-101"),
            models.Payload(id=6, event=way_event, type_id=5, value="true"),
            models.Payload(id=7, event=plan_event, type_id=6, value="A-0"),
        ])
        data_goals: list[models.Goal] = list([models.Goal(id=i, name=name) for i, name in goals.items()])
        data_roles: list[models.Role] = list([models.Role(id=i, name=name) for i, name in roles.items()])
        data_rights: list[models.Right] = list([models.Right(id=i, name=name) for i, name in rights.items()])
        db.add_all(data_goals)
        db.add_all(data_roles)
        db.add_all(data_rights)
        # await db.commit()
        data_role_right_goals: list[models.RoleRightGoal] = list(
            [models.RoleRightGoal(role_id=x[0], right_id=x[1], goal_id=x[2]) for x in roles_rights_goals]
        )
        db.add_all(data_role_right_goals)
        data_user: models.User = models.User(
            id=1,
            login="admin",
            hash=PasswordHash.recommended().hash("sidecuter"),
            token="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
        )
        db.add(data_user)
        data_user_without_roles: models.User = models.User(
            id=2,
            login="viewer",
            hash=PasswordHash.recommended().hash("sidecuter"),
            token="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ee"
        )
        db.add(data_user_without_roles)
        # await db.commit()
        data_user_roles: models.UserRole = models.UserRole(user_id=1, role_id=1)
        db.add(data_user_roles)

        # Добавляем навигационные данные для тестов
        # Location
        test_location = models.Location(
            id=1,
            id_sys="AV",
            name="Автозаводская",
            short="АВ",
            ready=True,
            address="ул. Автозаводская, д. 16",
            metro="Автозаводская",
            crossings=None,
            comments=None
        )
        db.add(test_location)

        # Corpus
        test_corpus = models.Corpus(
            id=1,
            id_sys="av-test",
            loc_id=1,
            name="Тестовый корпус",
            ready=True,
            stair_groups=None,
            comments=None
        )
        db.add(test_corpus)

        # Floor
        test_floor = models.Floor(
            id=1,
            name=1
        )
        db.add(test_floor)

        # Plan
        test_plan = models.Plan(
            id=1,
            id_sys="test-plan-1",
            cor_id=1,
            floor_id=1,
            ready=True,
            entrances="[]",
            graph="[]",
            svg_id=None,
            nearest_entrance=None,
            nearest_man_wc=None,
            nearest_woman_wc=None,
            nearest_shared_wc=None
        )
        db.add(test_plan)

        # Type
        test_type = models.Type(
            id=1,
            name="Учебная аудитория"
        )
        db.add(test_type)

        # Auditory
        test_auditory = models.Auditory(
            id=1,
            id_sys="test-101",
            type_id=1,
            ready=True,
            plan_id=1,
            name="101",
            text_from_sign=None,
            additional_info=None,
            comments=None,
            link=None
        )
        db.add(test_auditory)

        test_auditory_photo = models.AudPhoto(
            id=1,
            aud_id=1,
            ext="jpg",
            name="test-auditory-photo.jpg",
            path="/tmp/test-auditory-photo.jpg",
            link="/api/nav/auditory/photos/test-auditory-photo.jpg",
        )
        db.add(test_auditory_photo)

        # DOD navigation dataset
        dod_location = models.DodLocation(
            id=1,
            id_sys="DD",
            name="DOD Campus",
            short="DD",
            ready=True,
            address="dod address",
            metro="dod metro",
            crossings=None,
            comments="dod location",
        )
        db.add(dod_location)

        dod_corpus = models.DodCorpus(
            id=1,
            id_sys="dd-test",
            loc_id=1,
            name="DOD Corpus",
            ready=True,
            stair_groups=None,
            comments="dod corpus",
        )
        db.add(dod_corpus)

        dod_floor = models.DodFloor(
            id=1,
            name=1,
        )
        db.add(dod_floor)

        dod_static = models.DodStatic(
            id=1,
            ext="svg",
            path="/dod/plan.svg",
            name="dod-plan-svg",
            link="/static/dod-plan.svg",
        )
        db.add(dod_static)

        dod_plan = models.DodPlan(
            id=1,
            id_sys="dod-plan-1",
            cor_id=1,
            floor_id=1,
            ready=True,
            entrances="[]",
            graph="{}",
            svg_id=1,
            nearest_entrance=None,
            nearest_man_wc=None,
            nearest_woman_wc=None,
            nearest_shared_wc=None,
        )
        db.add(dod_plan)

        dod_type = models.DodType(
            id=1,
            name="DOD Type",
        )
        db.add(dod_type)

        dod_auditory = models.DodAuditory(
            id=1,
            id_sys="dod-101",
            type_id=1,
            ready=True,
            plan_id=1,
            name="D101",
            text_from_sign="dod sign",
            additional_info=None,
            comments="dod auditory",
            link=None,
        )
        db.add(dod_auditory)

        dod_auditory_photo = models.DodAudPhoto(
            id=1,
            aud_id=1,
            ext="png",
            name="dod-auditory-photo.png",
            path="/tmp/dod-auditory-photo.png",
            link="/api/dod/auditory/photos/dod-auditory-photo.png",
        )
        db.add(dod_auditory_photo)

        await db.commit()

    # Загружаем тестовое расписание в globals
    schedule_path = Path(__file__).parent / "schedule_test.json"
    json_text = schedule_path.read_text(encoding="utf-8")
    schedule = Schedule.model_validate_json(json_text)
    globals_.global_rasp = schedule.root
    globals_.locker = False

    # Инициализируем locationData для тестов
    from app.jobs.location_data.worker import fetch_location_data
    await fetch_location_data()


asyncio.run(create_db_and_tables())

client = TestClient(app)
