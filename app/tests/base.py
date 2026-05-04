import asyncio
import os
from pathlib import Path

# Должно стоять до любых импортов app.* — иначе get_settings() прочитает прод-конфиг.
os.environ["STATAPI_CONFIG"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config.test.yaml",
)

from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from pydantic import RootModel
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import models
from app.constants import (
    EVENT_TYPE_AUDS_ID,
    EVENT_TYPE_PLANS_ID,
    EVENT_TYPE_SITE_ID,
    EVENT_TYPE_WAYS_ID,
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_ENDPOINT_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_PLAN_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
)
from datetime import datetime
from pwdlib import PasswordHash
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from app.config import load_settings
from app.constants import REVIEW_STATUSES
from app.factory import AppFactory
from app.helpers.data import goals, rights, roles, roles_rights_goals
from app.jobs.location_data.worker import fetch_location_data
from app.models import Base
from app.schemas.rasp.schedule import Auditory
from app.tests.hooks import TestHooks

settings = load_settings()


class Schedule(RootModel[dict[str, Auditory]]):
    pass


# ── Тестовая БД: новый engine + session_maker, не общий с прод-кодом ─────────

db_path = settings.sqlalchemy_database_url.path.removeprefix("/")
try:
    os.remove(db_path)
except FileNotFoundError:
    pass

test_engine = create_async_engine(str(settings.sqlalchemy_database_url), future=True)
test_session_maker = async_sessionmaker(
    autoflush=True,
    autocommit=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# AppFactory + TestHooks: TestHooks в __init__ вызывает override_database,
# поэтому всё, что использует get_session_maker(), уже знает про тестовый engine.
app = AppFactory(TestHooks(test_session_maker))(settings)


async def create_db_and_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_session_maker.begin() as db:
        client: models.ClientId = models.ClientId(
            id=1,
            ident="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            creation_date=datetime(2026, 4, 25, 9, 0, 0),
        )
        second_client: models.ClientId = models.ClientId(
            id=2,
            ident="22e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            creation_date=datetime(2026, 4, 26, 9, 0, 0),
        )
        db.add_all([client, second_client])
        db.add_all(
            [
                models.EventType(id=EVENT_TYPE_SITE_ID, code_name="site", description="Посещения сайта"),
                models.EventType(id=EVENT_TYPE_AUDS_ID, code_name="auds", description="Поиск аудиторий"),
                models.EventType(id=EVENT_TYPE_WAYS_ID, code_name="ways", description="Построение маршрутов"),
                models.EventType(id=EVENT_TYPE_PLANS_ID, code_name="plans", description="Смена планов"),
            ]
        )
        db.add_all(
            [
                models.ValueType(id=1, name="string", description="Строковое значение"),
                models.ValueType(id=2, name="bool", description="Булево значение"),
            ]
        )
        db.add_all(
            [
                models.PayloadType(id=PAYLOAD_TYPE_ENDPOINT_ID, code_name="endpoint", value_type_id=1),
                models.PayloadType(id=PAYLOAD_TYPE_AUDITORY_ID, code_name="auditory_id", value_type_id=1),
                models.PayloadType(id=PAYLOAD_TYPE_START_ID, code_name="start_id", value_type_id=1),
                models.PayloadType(id=PAYLOAD_TYPE_END_ID, code_name="end_id", value_type_id=1),
                models.PayloadType(id=PAYLOAD_TYPE_SUCCESS_ID, code_name="success", value_type_id=2),
                models.PayloadType(id=PAYLOAD_TYPE_PLAN_ID, code_name="plan_id", value_type_id=1),
            ]
        )
        db.add_all(
            [
                models.AllowedPayload(event_type_id=EVENT_TYPE_SITE_ID, payload_type_id=PAYLOAD_TYPE_ENDPOINT_ID),
                models.AllowedPayload(event_type_id=EVENT_TYPE_AUDS_ID, payload_type_id=PAYLOAD_TYPE_AUDITORY_ID),
                models.AllowedPayload(event_type_id=EVENT_TYPE_AUDS_ID, payload_type_id=PAYLOAD_TYPE_SUCCESS_ID),
                models.AllowedPayload(event_type_id=EVENT_TYPE_WAYS_ID, payload_type_id=PAYLOAD_TYPE_START_ID),
                models.AllowedPayload(event_type_id=EVENT_TYPE_WAYS_ID, payload_type_id=PAYLOAD_TYPE_END_ID),
                models.AllowedPayload(event_type_id=EVENT_TYPE_WAYS_ID, payload_type_id=PAYLOAD_TYPE_SUCCESS_ID),
                models.AllowedPayload(event_type_id=EVENT_TYPE_PLANS_ID, payload_type_id=PAYLOAD_TYPE_PLAN_ID),
            ]
        )
        db.add_all(
            [
                models.Event(
                    id=1,
                    client_id=1,
                    event_type_id=EVENT_TYPE_AUDS_ID,
                    trigger_time=datetime(2026, 4, 25, 10, 0, 0),
                ),
                models.Event(
                    id=2,
                    client_id=1,
                    event_type_id=EVENT_TYPE_WAYS_ID,
                    trigger_time=datetime(2026, 4, 25, 11, 0, 0),
                ),
                models.Event(
                    id=3,
                    client_id=2,
                    event_type_id=EVENT_TYPE_WAYS_ID,
                    trigger_time=datetime(2026, 4, 26, 11, 0, 0),
                ),
                models.Event(
                    id=4,
                    client_id=2,
                    event_type_id=EVENT_TYPE_SITE_ID,
                    trigger_time=datetime(2026, 4, 26, 12, 0, 0),
                ),
            ]
        )
        db.add_all(
            [
                models.Payload(id=1, event_id=1, type_id=PAYLOAD_TYPE_AUDITORY_ID, value="a-100"),
                models.Payload(id=2, event_id=1, type_id=PAYLOAD_TYPE_SUCCESS_ID, value="true"),
                models.Payload(id=3, event_id=2, type_id=PAYLOAD_TYPE_START_ID, value="a-100"),
                models.Payload(id=4, event_id=2, type_id=PAYLOAD_TYPE_END_ID, value="a-101"),
                models.Payload(id=5, event_id=2, type_id=PAYLOAD_TYPE_SUCCESS_ID, value="true"),
                models.Payload(id=6, event_id=3, type_id=PAYLOAD_TYPE_START_ID, value="a-101"),
                models.Payload(id=7, event_id=3, type_id=PAYLOAD_TYPE_END_ID, value="a-102"),
                models.Payload(id=8, event_id=3, type_id=PAYLOAD_TYPE_SUCCESS_ID, value="false"),
                models.Payload(id=9, event_id=4, type_id=PAYLOAD_TYPE_ENDPOINT_ID, value="/api/get/route"),
            ]
        )
        review_statuses: list[models.ReviewStatus] = list([
            models.ReviewStatus(id=id_, name=name) for id_, name in REVIEW_STATUSES.items()
        ])
        db.add_all(review_statuses)
        db.add_all(
            [
                models.Problem(id="way"),
                models.Problem(id="other"),
                models.Problem(id="plan"),
                models.Problem(id="work"),
            ]
        )
        db.add(
            models.Review(
                id=1,
                client_id=1,
                problem_id="way",
                text="test review",
                review_status_id=1,
                creation_date=datetime(2026, 4, 25, 12, 0, 0),
            )
        )

        data_goals: list[models.Goal] = list([models.Goal(id=i, name=name) for i, name in goals.items()])
        data_roles: list[models.Role] = list([models.Role(id=i, name=name) for i, name in roles.items()])
        data_rights: list[models.Right] = list([models.Right(id=i, name=name) for i, name in rights.items()])
        db.add_all(data_goals)
        db.add_all(data_roles)
        db.add_all(data_rights)
        data_role_right_goals: list[models.RoleRightGoal] = list(
            [models.RoleRightGoal(role_id=x[0], right_id=x[1], goal_id=x[2], can_grant=x[0] == 1) for x in roles_rights_goals]
        )
        db.add_all(data_role_right_goals)
        data_user: models.User = models.User(
            id=1,
            login="admin",
            hash=PasswordHash.recommended().hash("sidecuter"),
            token="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
        )
        db.add(data_user)
        data_user_roles: models.UserRole = models.UserRole(user_id=1, role_id=1)
        db.add(data_user_roles)

        # Навигационные данные
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

        test_floor = models.Floor(
            id=1,
            name=1
        )
        db.add(test_floor)

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

        test_type = models.Type(
            id=1,
            name="Учебная аудитория"
        )
        db.add(test_type)

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

        # DOD-данные
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

    # Загружаем тестовое расписание прямо в state приложения.
    schedule_path = Path(__file__).parent / "schedule_test.json"
    json_text = schedule_path.read_text(encoding="utf-8")
    schedule = Schedule.model_validate_json(json_text)
    app.state.app_state.global_rasp = schedule.root

    # Инициализируем locationData (читает БД через override_database).
    await fetch_location_data(state=app.state.app_state)


asyncio.run(create_db_and_tables())

client = TestClient(app)
