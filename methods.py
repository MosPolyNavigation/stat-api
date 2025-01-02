from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import ScalarResult
from sqlalchemy import Select
from typing import TypeVar
import models
import schemas

T = TypeVar('T', bound=models.Base)


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


async def item_pagination(
        db: Session,
        data_model: T,
        params: schemas.StatisticsBase
) -> tuple[ScalarResult | schemas.Status, int]:
    query = Select(data_model)
    if params.page is not None and params.per_page is not None:
        query = query.offset(params.per_page*(params.page-1)).limit(params.per_page)
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    try:
        return db.execute(query).scalars(), 200
    except SQLAlchemyError as e:
        return schemas.Status(status=str(e)), 500
