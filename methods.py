from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Select
import models
import schemas


async def create_uuid(db: Session) -> schemas.UserId:
    item = models.UserId()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


async def insert_site_stat(db: Session, data: schemas.SiteStat) -> tuple[schemas.Status, int]:
    try:
        user = db.execute(Select(models.UserId).filter_by(id=data.user_id)).scalar_one()
        item = models.SiteStat(user=user, endpoint=data.endpoint)
        db.add(item)
        db.commit()
    except SQLAlchemyError:
        return schemas.Status(status="Nope"), 500
    return schemas.Status(), 200


async def insert_aud_selection(db: Session, data: schemas.SelectedAuditory) -> tuple[schemas.Status, int]:
    try:
        user = db.execute(Select(models.UserId).filter_by(id=data.user_id)).scalar_one()
        auditory = db.execute(Select(models.Auditory).filter_by(id=data.auditory_id)).scalar_one()
        item = models.SelectAuditory(user=user, auditory=auditory, success=data.success)
        db.add(item)
        db.commit()
    except SQLAlchemyError:
        return schemas.Status(status="Nope"), 500
    return schemas.Status(), 200
