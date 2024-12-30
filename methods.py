from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Select
import models
import schemas


async def create_uuid(db: Session) -> schemas.UUID:
    item = models.UUID()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


async def insert_site_stat(db: Session, data: schemas.SiteStat) -> tuple[schemas.Status, int]:
    try:
        uuid = db.execute(Select(models.UUID).filter_by(id=data.uuid)).fetchone()
        item = models.SiteStat(uuid=uuid, endpoint=data.endpoint)
        db.add(item)
        db.commit()
    except SQLAlchemyError:
        return schemas.Status(status="Nope"), 500
    return schemas.Status(), 200


async def insert_aud_selection(db: Session, data: schemas.SelectedAuditory) -> tuple[schemas.Status, int]:
    try:
        uuid = db.execute(Select(models.UUID).filter_by(id=data.uuid)).fetchone()
        auditory = db.execute(Select(models.Auditory).filter_by(id=data.auditory)).fetchone()
        item = models.SelectAuditory(uuid=uuid, auditory=auditory, success=data.success)
        db.add(item)
        db.commit()
    except SQLAlchemyError:
        return schemas.Status(status="Nope"), 500
    return schemas.Status(), 200
