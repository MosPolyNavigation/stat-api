"""Обработчики вставки статистических данных и карт этажей."""

from os import path

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.helpers.errors import LookupException


async def insert_site_stat(db: AsyncSession, data: schemas.SiteStatIn) -> schemas.Status:
    """Записывает факт посещения раздела сайта конкретным пользователем."""
    user = (await db.execute(Select(models.UserId).filter_by(user_id=data.user_id))).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.SiteStat(user=user, endpoint=data.endpoint)
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_aud_selection(db: AsyncSession, data: schemas.SelectedAuditoryIn) -> schemas.Status:
    """Фиксирует выбор аудитории пользователем и успешность построения маршрута."""
    user = (await db.execute(Select(models.UserId).filter_by(user_id=data.user_id))).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.SelectAuditory(
        user=user,
        auditory_id=data.auditory_id,
        success=data.success,
    )
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_start_way(db: AsyncSession, data: schemas.StartWayIn) -> schemas.Status:
    """Записывает попытку построения маршрута между аудиториями."""
    user = (await db.execute(Select(models.UserId).filter_by(user_id=data.user_id))).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.StartWay(
        user=user,
        start_id=data.start_id,
        end_id=data.end_id,
        success=data.success,
    )
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_changed_plan(db: AsyncSession, data: schemas.ChangePlanIn) -> schemas.Status:
    """Фиксирует переход пользователя на другой план корпуса."""
    user = (await db.execute(Select(models.UserId).filter_by(user_id=data.user_id))).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.ChangePlan(user=user, plan_id=data.plan_id)
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_floor_map(
    db: AsyncSession,
    full_file_name: str,
    file_path: str,
    campus: str,
    corpus: str,
    floor: int,
):
    """Добавляет в базу новый файл плана этажа."""
    file_name, file_extension = path.splitext(full_file_name)

    item = models.FloorMap(
        floor=floor,
        campus=campus,
        corpus=corpus,
        file_path=file_path,
        file_name=file_name.lower(),
        file_extension=file_extension.lower(),
    )

    db.add(item)
    await db.commit()
