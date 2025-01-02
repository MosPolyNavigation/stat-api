from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Select
import models
import schemas


async def create_uuid(db: Session) -> tuple[schemas.UserId | schemas.Status, int]:
    try:
        item = models.UserId()
        db.add(item)
        db.commit()
        db.refresh(item)
        return item, 200
    except SQLAlchemyError as e:
        return schemas.Status(status=str(e)), 500


async def insert_site_stat(db: Session, data: schemas.SiteStat) -> tuple[schemas.Status, int]:
    user = db.execute(Select(models.UserId).filter_by(user_id=data.user_id)).scalar_one_or_none()
    if user is None:
        return schemas.Status(status="User not found"), 404
    try:
        item = models.SiteStat(user=user, endpoint=data.endpoint)
        db.add(item)
        db.commit()
    except SQLAlchemyError as e:
        return schemas.Status(status=str(e)), 500
    return schemas.Status(), 200


async def insert_aud_selection(db: Session, data: schemas.SelectedAuditory) -> tuple[schemas.Status, int]:
    user = db.execute(Select(models.UserId).filter_by(user_id=data.user_id)).scalar_one_or_none()
    auditory = db.execute(Select(models.Auditory).filter_by(id=data.auditory_id)).scalar_one_or_none()
    if user is None:
        return schemas.Status(status="User not found"), 404
    if auditory is None:
        return schemas.Status(status="Auditory not found"), 404
    try:
        item = models.SelectAuditory(user=user, auditory=auditory, success=data.success)
        db.add(item)
        db.commit()
    except SQLAlchemyError as e:
        return schemas.Status(status=str(e)), 500
    return schemas.Status(), 200
