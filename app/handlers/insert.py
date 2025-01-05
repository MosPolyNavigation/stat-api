from sqlalchemy.orm import Session
from sqlalchemy import Select
from app import schemas, models
from app.helpers.errors import LookupException


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


async def insert_changed_plan(db: Session, data: schemas.ChangePlanIn) -> schemas.Status:
    user = db.execute(Select(models.UserId).filter_by(user_id=data.user_id)).scalar_one_or_none()
    plan = db.execute(Select(models.Plan).filter_by(id=data.plan_id)).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    if plan is None:
        raise LookupException("Changed plan")
    item = models.ChangePlan(user=user, plan=plan)
    db.add(item)
    db.commit()
    return schemas.Status()
