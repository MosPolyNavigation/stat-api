from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.errors import LookupException
from sqlalchemy import Select
from typing import TypeVar
from app.state import *
from app import models
from app import schemas

T = TypeVar('T', bound=models.Base)


async def create_user_id(db: Session) -> schemas.UserId:
    item = models.UserId()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


async def insert_site_stat(db: Session, data: schemas.SiteStatIn) -> schemas.Status:
    user = db.execute(Select(models.UserId).filter_by(user_id=data.user_id)).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.SiteStat(user=user, endpoint=data.endpoint)
    db.add(item)
    db.commit()
    return schemas.Status()


async def insert_aud_selection(db: Session, data: schemas.SelectedAuditoryIn) -> schemas.Status:
    user = db.execute(Select(models.UserId).filter_by(user_id=data.user_id)).scalar_one_or_none()
    auditory = db.execute(Select(models.Auditory).filter_by(id=data.auditory_id)).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    if auditory is None:
        raise LookupException("Auditory")
    item = models.SelectAuditory(user=user, auditory=auditory, success=data.success)
    db.add(item)
    db.commit()
    return schemas.Status()


async def insert_start_way(db: Session, data: schemas.StartWayIn) -> schemas.Status:
    user = db.execute(Select(models.UserId).filter_by(user_id=data.user_id)).scalar_one_or_none()
    start = db.execute(Select(models.Auditory).filter_by(id=data.start_id)).scalar_one_or_none()
    end = db.execute(Select(models.Auditory).filter_by(id=data.end_id)).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    if start is None:
        raise LookupException("Start auditory")
    if end is None:
        raise LookupException("End auditory")
    item = models.StartWay(user=user, start=start, end=end)
    db.add(item)
    db.commit()
    return schemas.Status()


async def item_pagination(
        data_model: T,
        params: schemas.Filter
) -> Select:
    query = Select(data_model)
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    return query


def check_user(state: AppState, user_id) -> float:
    state.user_access.setdefault(user_id, datetime.now() - timedelta(seconds=1))
    delta = datetime.now() - state.user_access[user_id]
    state.user_access[user_id] = datetime.now()
    return delta.total_seconds()
