import os
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.config import get_settings
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

path = get_settings().sqlalchemy_database_url.path.removeprefix("/")
try:
    os.remove(path)
except FileNotFoundError:
    pass

from app.tests.app import app
from app.models import Base
from app.database import engine, get_db
from app.helpers.data import goals, roles, rights, roles_rights_goals
from app import models

add_pagination(app)


def create_db_and_tables():
    Base.metadata.create_all(engine)
    db: Session = get_db().__next__()
    user: models.UserId = models.UserId(
        user_id="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec"
    )
    db.add(user)
    db.commit()
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
    db.commit()
    data_start_way = models.StartWay(
        user=user, start_id="a-100", end_id="a-101"
    )
    db.add(data_start_way)
    db.commit()
    data_select_aud = models.SelectAuditory(user=user, auditory_id="a-100")
    db.add(data_select_aud)
    db.commit()
    data_change_plan = models.ChangePlan(user=user, plan_id="A-0")
    db.add(data_change_plan)
    db.commit()
    data_goals: list[models.Goal] = list([models.Goal(id=i, name=name) for i, name in goals.items()])
    data_roles: list[models.Role] = list([models.Role(id=i, name=name) for i, name in roles.items()])
    data_rights: list[models.Right] = list([models.Right(id=i, name=name) for i, name in rights.items()])
    db.add_all(data_goals)
    db.add_all(data_roles)
    db.add_all(data_rights)
    db.commit()
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
    db.commit()
    data_user_roles: models.UserRole = models.UserRole(user_id=1, role_id=1)
    db.add(data_user_roles)
    db.commit()


create_db_and_tables()


client = TestClient(app)
