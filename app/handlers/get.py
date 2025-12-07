"""Обработчики для получения статистики и популярных аудиторий."""

from datetime import date
from typing import Dict

from sqlalchemy import Select, case, func, select, union_all, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app import models, schemas
from .filter import filter_by_date


async def get_endpoint_stats(db: AsyncSession, params: schemas.FilterQuery) -> list[schemas.Statistics]:
    """
    Возвращает статистику посещений выбранного раздела за период.

    Считает общее количество запросов, уникальных пользователей и новых пользователей.
    """
    borders = filter_by_date(params)
    visit_date_expr = func.date(params.model.visit_date)
    visit_date_out_expr = func.cast(visit_date_expr, String)
    query = (
        select(
            visit_date_out_expr.label("period_str"),
            func.count(params.model.user_id).label("all_visits"),
            func.count(params.model.user_id.distinct()).label("visitor_count"),
            func.count(
                case((func.date(models.UserId.creation_date) == visit_date_expr, models.UserId.user_id)).distinct()
            ).label("unique_visits"),
        )
        .select_from(params.model)
        .join(models.UserId, params.model.user_id == models.UserId.user_id)
        .group_by(visit_date_out_expr)
        .order_by(visit_date_out_expr)
    )
    if borders is not None:
        query = query.where(params.model.visit_date >= borders[0]).where(params.model.visit_date < borders[1])
    rows = (await db.execute(query)).fetchall()
    return [
        schemas.Statistics(
            period=date.fromisoformat(row.period_str),
            all_visits=row.all_visits,
            visitor_count=row.visitor_count,
            unique_visitors=row.unique_visits,
        )
        for row in rows
    ]


def get_popular_auds_query():
    """Формирует запрос на поиск популярных аудиторий."""
    return aliased(
        union_all(
            Select(models.SelectAuditory.auditory_id.label("ID"), func.count().label("CNT"))
            .select_from(models.SelectAuditory)
            .filter_by(success=True)
            .group_by(models.SelectAuditory.auditory_id.label("ID")),
            Select(models.StartWay.start_id.label("ID"), func.count().label("CNT") * 3)
            .select_from(models.StartWay)
            .group_by(models.StartWay.start_id.label("ID")),
            Select(models.StartWay.end_id.label("ID"), func.count().label("CNT") * 3)
            .select_from(models.StartWay)
            .group_by(models.StartWay.end_id.label("ID")),
        ).alias("tr")
    )


async def get_popular_auds(db: AsyncSession) -> list[str]:
    """Возвращает список ID аудиторий, отсортированный по популярности."""
    tr = get_popular_auds_query()
    query = Select(tr.c.ID).select_from(tr).group_by(tr.c.ID).order_by(func.sum(tr.c.CNT).desc())
    popular = (await db.execute(query)).scalars().all()
    return popular


async def get_popular_auds_with_count(db: AsyncSession):
    """Возвращает пары (ID, количество баллов популярности)."""
    tr = get_popular_auds_query()
    query = Select(tr.c.ID, func.sum(tr.c.CNT)).select_from(tr).group_by(tr.c.ID).order_by(func.sum(tr.c.CNT).desc())
    with_count = (await db.execute(query)).fetchall()
    return with_count


async def get_all_floor_maps(db: AsyncSession) -> Dict[str, Dict[str, Dict[int, str]]]:
    """Возвращает карту путей к файлам этажей сгруппированную по кампусу/корпусу/этажу."""
    maps = (await db.execute(Select(models.floor_map.FloorMap))).all()
    result: Dict[str, Dict[str, Dict[int, str]]] = {}

    for floor_map in maps:
        campus = floor_map.campus
        corpus = floor_map.corpus
        floor = floor_map.floor
        file_path = floor_map.file_path

        if campus not in result:
            result[campus] = {}

        if corpus not in result[campus]:
            result[campus][corpus] = {}

        result[campus][corpus][floor] = file_path

    return result
