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
        user: models.UserId = models.UserId(
            user_id="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec"
        )
        db.add(user)
        review_statuses: list[models.ReviewStatus] = list([
            models.ReviewStatus(id=id_, name=name) for id_, name in REVIEW_STATUSES.items()
        ])
        db.add_all(review_statuses)
        data_site_stat = models.SiteStat(user=user)
        db.add(data_site_stat)
        data_start_way = models.StartWay(
            user=user, start_id="a-100", end_id="a-101"
        )
        db.add(data_start_way)
        data_select_aud = models.SelectAuditory(user=user, auditory_id="a-100")
        db.add(data_select_aud)
        data_change_plan = models.ChangePlan(user=user, plan_id="A-0")
        db.add(data_change_plan)
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
