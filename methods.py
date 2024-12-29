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
