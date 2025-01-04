import os
from app.config import get_settings

path = get_settings().sqlalchemy_database_url.path.removeprefix("/")
try:
    os.remove(path)
except FileNotFoundError:
    pass

from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from app.app import app
from app.models import Base
from app.database import engine, get_db
from sqlalchemy.orm import Session
from app.helpers.data import auds, plans
from app import models

add_pagination(app)


def create_db_and_tables():
    Base.metadata.create_all(engine)
    db: Session = get_db().__next__()
    user: models.UserId = models.UserId(user_id="11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec")
    db.add(user)
    db.commit()
    plans_data: list[models.Plan] = list(map(lambda x: models.Plan(id=x), list(set(plans.split('\n')))))
    db.add_all(plans_data)
    db.commit()
    auds_data: list[models.Auditory] = list(map(lambda x: models.Auditory(id=x), list(set(auds.split('\n')))))
    db.add_all(auds_data)
    db.commit()


create_db_and_tables()


client = TestClient(app)
