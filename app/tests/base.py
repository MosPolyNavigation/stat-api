import asyncio
import os
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
        user: models.UserId = models.UserId(
            user_id="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec"
        )
        db.add(user)
        review_statuses: list[models.ReviewStatus] = list([
            models.ReviewStatus(id=id_, name=name) for id_, name in review_status.items()
        ])
        db.add_all(review_statuses)
        # await db.commit()
        # plans_data: list[models.Plan] = list(map(
        #     lambda x: models.Plan(id=x),
        #     list(set(plans.split('\n')))
        # ))
        # db.add_all(plans_data)
        # db.commit()
        # auds_data: list[models.Auditory] = list(map(
        #     lambda x: models.Auditory(id=x),
        #     list(set(auds.split('\n')))
        # ))
        # db.add_all(auds_data)
        # db.commit()
        data_site_stat = models.SiteStat(user=user)
        db.add(data_site_stat)
        # await db.commit()
        data_start_way = models.StartWay(
            user=user, start_id="a-100", end_id="a-101"
        )
        db.add(data_start_way)
        # await db.commit()
        data_select_aud = models.SelectAuditory(user=user, auditory_id="a-100")
        db.add(data_select_aud)
        # await db.commit()
        data_change_plan = models.ChangePlan(user=user, plan_id="A-0")
        db.add(data_change_plan)
        # await db.commit()
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
        # await db.commit()
        data_user_roles: models.UserRole = models.UserRole(user_id=1, role_id=1)
        db.add(data_user_roles)

        # Ð”Ð¾Ð±Ð°Ð²Ð»ÑÐµÐ¼ Ð½Ð°Ð²Ð¸Ð³Ð°Ñ†Ð¸Ð¾Ð½Ð½Ñ‹Ðµ Ð´Ð°Ð½Ð½Ñ‹Ðµ Ð´Ð»Ñ Ñ‚ÐµÑÑ‚Ð¾Ð²
        # Location
        test_location = models.Location(
            id=1,
            id_sys="AV",
            name="ÐÐ²Ñ‚Ð¾Ð·Ð°Ð²Ð¾Ð´ÑÐºÐ°Ñ",
            short="ÐÐ’",
            ready=True,
            address="ÑƒÐ». ÐÐ²Ñ‚Ð¾Ð·Ð°Ð²Ð¾Ð´ÑÐºÐ°Ñ, Ð´. 16",
            metro="ÐÐ²Ñ‚Ð¾Ð·Ð°Ð²Ð¾Ð´ÑÐºÐ°Ñ",
            crossings=None,
            comments=None
        )
        db.add(test_location)

        # Corpus
        test_corpus = models.Corpus(
            id=1,
            id_sys="av-test",
            loc_id=1,
            name="Ð¢ÐµÑÑ‚Ð¾Ð²Ñ‹Ð¹ ÐºÐ¾Ñ€Ð¿ÑƒÑ",
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
            name="Ð£Ñ‡ÐµÐ±Ð½Ð°Ñ Ð°ÑƒÐ´Ð¸Ñ‚Ð¾Ñ€Ð¸Ñ"
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

        await db.commit()

    # Ð—Ð°Ð³Ñ€ÑƒÐ¶Ð°ÐµÐ¼ Ñ‚ÐµÑÑ‚Ð¾Ð²Ð¾Ðµ Ñ€Ð°ÑÐ¿Ð¸ÑÐ°Ð½Ð¸Ðµ Ð² globals
    schedule_path = Path(__file__).parent / "schedule_test.json"
    json_text = schedule_path.read_text(encoding="utf-8")
    schedule = Schedule.model_validate_json(json_text)
    globals_.global_rasp = schedule.root
    globals_.locker = False

    # Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð¸Ñ€ÑƒÐµÐ¼ locationData Ð´Ð»Ñ Ñ‚ÐµÑÑ‚Ð¾Ð²
    from app.jobs.location_data.worker import fetch_location_data
    await fetch_location_data()


asyncio.run(create_db_and_tables())

client = TestClient(app)


