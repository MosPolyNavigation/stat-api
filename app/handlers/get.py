from datetime import datetime
from typing import Optional

from sqlalchemy import String, bindparam, case, cast, distinct, func, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.constants import (
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
)


def _period_expression(period_type: str):
    trigger_time = cast(models.Event.trigger_time, String)
    if period_type == "day":
        return func.substr(trigger_time, 1, 10)
    if period_type == "month":
        return func.substr(trigger_time, 1, 7)
    if period_type == "year":
        return func.substr(trigger_time, 1, 4)
    raise ValueError("period_type должен быть одним из: day, month, year")


def _unique_visitor_expression(period_type: str, period):
    client_creation = cast(models.ClientId.creation_date, String)
    if period_type == "day":
        client_period = func.substr(client_creation, 1, 10)
    elif period_type == "month":
        client_period = func.substr(client_creation, 1, 7)
    elif period_type == "year":
        client_period = func.substr(client_creation, 1, 4)
    else:
        raise ValueError("period_type должен быть одним из: day, month, year")
    return case(
        (
            client_period == period,
            models.Event.client_id,
        ),
        else_=None,
    )


def _format_period(period_type: str, period: str) -> str:
    if period_type == "day":
        return period
    if period_type == "month":
        return f"{period}-01"
    if period_type == "year":
        return f"{period}-01-01"
    raise ValueError("period_type должен быть одним из: day, month, year")


async def get_popular_audiences(
    db: AsyncSession,
    limit: int = 100,
) -> list[schemas.PopularAudience]:
    success_event_ids = (
        select(models.Payload.event_id)
        .where(models.Payload.type_id == PAYLOAD_TYPE_SUCCESS_ID)
        .where(func.lower(models.Payload.value) == "true")
    )
    weight = case(
        (models.Payload.type_id == PAYLOAD_TYPE_AUDITORY_ID, 1),
        (models.Payload.type_id.in_([PAYLOAD_TYPE_START_ID, PAYLOAD_TYPE_END_ID]), 3),
        else_=0,
    )
    rows = (
        await db.execute(
            select(
                models.Payload.value.label("auditory_id"),
                func.sum(weight).label("total_weight"),
            )
            .where(
                models.Payload.type_id.in_(
                    [
                        PAYLOAD_TYPE_AUDITORY_ID,
                        PAYLOAD_TYPE_START_ID,
                        PAYLOAD_TYPE_END_ID,
                    ]
                )
            )
            .where(models.Payload.event_id.in_(success_event_ids))
            .group_by(models.Payload.value)
            .order_by(func.sum(weight).desc())
            .limit(limit)
        )
    ).all()

    return [
        schemas.PopularAudience(
            auditory_id=str(row.auditory_id),
            total_weight=int(row.total_weight or 0),
        )
        for row in rows
    ]


async def get_period_stats(
    db: AsyncSession,
    period_type: str,
    start: datetime,
    end: datetime,
    event_type_id: Optional[int] = None,
) -> list[schemas.Statistics]:
    period = _period_expression(period_type).label("period")
    event_type_id_param = bindparam("event_type_id", value=event_type_id)
    unique_visitor = _unique_visitor_expression(period_type, period)

    statement = (
        select(
            period,
            func.count().label("all_visits"),
            func.count(distinct(models.Event.client_id)).label("visitor_count"),
            func.count(distinct(unique_visitor)).label("unique_visitors"),
        )
        .join(models.ClientId, models.ClientId.id == models.Event.client_id)
        .where(models.Event.trigger_time >= start)
        .where(models.Event.trigger_time < end)
        .where(
            (event_type_id_param.is_(None))
            | (models.Event.event_type_id == event_type_id_param)
        )
    )
    statement = statement.group_by(period).order_by(period)

    rows = (await db.execute(statement)).all()
    return [
        schemas.Statistics(
            period=_format_period(period_type, str(row.period)),
            all_visits=int(row.all_visits or 0),
            visitor_count=int(row.visitor_count or 0),
            unique_visitors=int(row.unique_visitors or 0),
        )
        for row in rows
    ]


async def get_aggregated_stats(
    db: AsyncSession,
    period_type: str,
    start: datetime,
    end: datetime,
    event_type_id: Optional[int] = None,
) -> schemas.AggregatedStatistics:
    period = _period_expression(period_type).label("period")
    event_type_id_param = bindparam("event_type_id", value=event_type_id)

    base_filters = (
        models.Event.trigger_time >= start,
        models.Event.trigger_time < end,
        (event_type_id_param.is_(None))
        | (models.Event.event_type_id == event_type_id_param),
    )
    unique_visitor = _unique_visitor_expression(period_type, period)

    period_stats = (
        select(
            period,
            func.count().label("all_visits"),
            func.count(distinct(models.Event.client_id)).label("visitor_count"),
            func.count(distinct(unique_visitor)).label("unique_visitors"),
        )
        .join(models.ClientId, models.ClientId.id == models.Event.client_id)
        .where(*base_filters)
        .group_by(period)
        .cte("period_stats")
    )
    global_stats = (
        select(
            func.count(distinct(models.Event.client_id)).label("total_visitor_count"),
            func.count(distinct(unique_visitor)).label("total_unique_visitors"),
        )
        .join(models.ClientId, models.ClientId.id == models.Event.client_id)
        .where(*base_filters)
        .cte("global_stats")
    )
    period_agg = (
        select(
            func.sum(period_stats.c.all_visits).label("total_all_visits"),
            func.round(
                func.avg(period_stats.c.all_visits),
                1,
            ).label("avg_all_visits_per_period"),
            func.round(
                func.avg(period_stats.c.visitor_count),
                1,
            ).label("avg_visitor_count_per_period"),
            func.round(
                func.avg(period_stats.c.unique_visitors),
                1,
            ).label("avg_unique_visitors_per_period"),
            func.count().label("entries_analyzed"),
        )
        .select_from(period_stats)
        .cte("period_agg")
    )
    row = (
        await db.execute(
            select(
                period_agg.c.total_all_visits,
                period_agg.c.avg_all_visits_per_period,
                period_agg.c.avg_visitor_count_per_period,
                period_agg.c.avg_unique_visitors_per_period,
                period_agg.c.entries_analyzed,
                global_stats.c.total_visitor_count,
                global_stats.c.total_unique_visitors,
            ).select_from(period_agg.join(global_stats, true()))
        )
    ).one()

    return schemas.AggregatedStatistics(
        total_all_visits=int(row.total_all_visits or 0),
        total_visitor_count=int(row.total_visitor_count or 0),
        total_unique_visitors=int(row.total_unique_visitors or 0),
        avg_all_visits_per_day=float(row.avg_all_visits_per_period or 0),
        avg_visitor_count_per_day=float(row.avg_visitor_count_per_period or 0),
        avg_unique_visitors_per_day=float(row.avg_unique_visitors_per_period or 0),
        entries_analized=int(row.entries_analyzed or 0),
    )
