from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.constants import (
    EVENT_TYPE_IDS_BY_CODE,
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
)


def _period_expression(period_type: str):
    if period_type == "day":
        return func.strftime("%Y-%m-%d", models.Event.trigger_time)
    if period_type == "month":
        return func.strftime("%Y-%m", models.Event.trigger_time)
    if period_type == "year":
        return func.strftime("%Y", models.Event.trigger_time)
    raise ValueError("period_type must be one of: day, month, year")


def _postgres_period_expression(period_type: str):
    if period_type == "day":
        return func.to_char(models.Event.trigger_time, "YYYY-MM-DD")
    if period_type == "month":
        return func.to_char(models.Event.trigger_time, "YYYY-MM")
    if period_type == "year":
        return func.to_char(models.Event.trigger_time, "YYYY")
    raise ValueError("period_type must be one of: day, month, year")


def _period_expression_for_session(db: AsyncSession, period_type: str):
    dialect = db.bind.dialect.name if db.bind is not None else ""
    if dialect == "postgresql":
        return _postgres_period_expression(period_type)
    return _period_expression(period_type)


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
            .order_by(func.sum(weight).desc(), models.Payload.value.asc())
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
    period = _period_expression_for_session(db, period_type).label("period")
    event_day = func.date(models.Event.trigger_time)
    client_creation_day = func.date(models.ClientId.creation_date)

    statement = (
        select(
            period,
            func.count(models.Event.id).label("all_visits"),
            func.count(distinct(models.Event.client_id)).label("visitor_count"),
            func.count(
                distinct(
                    case(
                        (
                            client_creation_day == event_day,
                            models.Event.client_id,
                        ),
                        else_=None,
                    )
                )
            ).label("unique_visitors"),
        )
        .join(models.ClientId, models.ClientId.id == models.Event.client_id)
        .where(models.Event.trigger_time >= start)
        .where(models.Event.trigger_time < end)
    )
    if event_type_id is not None:
        statement = statement.where(models.Event.event_type_id == event_type_id)
    statement = statement.group_by(period).order_by(period)

    rows = (await db.execute(statement)).all()
    return [
        schemas.Statistics(
            period=str(row.period),
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
    stats = await get_period_stats(db, period_type, start, end, event_type_id)
    entries = len(stats)

    total_all_visits = sum(item.all_visits for item in stats)
    total_visitor_count = sum(item.visitor_count for item in stats)
    total_unique_visitors = sum(item.unique_visitors for item in stats)

    return schemas.AggregatedStatistics(
        total_all_visits=total_all_visits,
        total_visitor_count=total_visitor_count,
        total_unique_visitors=total_unique_visitors,
        avg_all_visits_per_day=round(total_all_visits / entries, 1) if entries else 0,
        avg_visitor_count_per_day=round(total_visitor_count / entries, 1) if entries else 0,
        avg_unique_visitors_per_day=round(total_unique_visitors / entries, 1) if entries else 0,
        entries_analized=entries,
    )


def _stats_window_from_filter(
    params: schemas.FilterQuery,
) -> tuple[str, datetime, datetime]:
    if params.start_date is not None and params.end_date is not None:
        return (
            "day",
            datetime.combine(params.start_date, time.min),
            datetime.combine(params.end_date + timedelta(days=1), time.min),
        )
    if params.start_month is not None and params.end_month is not None:
        start = datetime.strptime(params.start_month, "%Y-%m")
        end_month = datetime.strptime(params.end_month, "%Y-%m")
        end = datetime(end_month.year + (end_month.month == 12), end_month.month % 12 + 1, 1)
        return "month", start, end
    if params.start_year is not None and params.end_year is not None:
        start = datetime.strptime(params.start_year, "%Y")
        end = datetime(int(params.end_year) + 1, 1, 1)
        return "year", start, end
    today = date.today()
    return (
        "day",
        datetime.combine(today, time.min),
        datetime.combine(today + timedelta(days=1), time.min),
    )


async def get_endpoint_stats(
    db: AsyncSession,
    params: schemas.FilterQuery,
) -> list[schemas.Statistics]:
    period_type, start, end = _stats_window_from_filter(params)
    return await get_period_stats(
        db,
        period_type=period_type,
        start=start,
        end=end,
        event_type_id=EVENT_TYPE_IDS_BY_CODE[params.target.value],
    )


async def get_agr_endp_stats(
    db: AsyncSession,
    params: schemas.FilterQuery,
) -> schemas.AggregatedStatistics:
    period_type, start, end = _stats_window_from_filter(params)
    return await get_aggregated_stats(
        db,
        period_type=period_type,
        start=start,
        end=end,
        event_type_id=EVENT_TYPE_IDS_BY_CODE[params.target.value],
    )
