from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import case, desc, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.constants import (
    EVENT_TYPE_IDS_BY_CODE,
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
)
from app.models import ClientId, Event, Payload


def _empty_aggregated_statistics() -> schemas.AggregatedStatistics:
    return schemas.AggregatedStatistics(
        total_all_visits=0,
        total_unique_visitors=0,
        total_visitor_count=0,
        avg_all_visits_per_day=0.0,
        avg_unique_visitors_per_day=0.0,
        avg_visitor_count_per_day=0.0,
        entries_analized=0,
    )


def _as_start_datetime(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, datetime.min.time())


def _as_end_datetime(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.combine(value + timedelta(days=1), datetime.min.time())


def _period_expression(period_type: str, dialect_name: str):
    if period_type not in {"day", "month", "year"}:
        raise ValueError("period_type must be one of: day, month, year")

    if dialect_name == "sqlite":
        formats = {
            "day": "%Y-%m-%d",
            "month": "%Y-%m",
            "year": "%Y",
        }
        return func.strftime(formats[period_type], Event.trigger_time)

    formats = {
        "day": "YYYY-MM-DD",
        "month": "YYYY-MM",
        "year": "YYYY",
    }
    return func.to_char(Event.trigger_time, formats[period_type])


async def get_popular_audiences(
    db: AsyncSession,
    limit: int = 100,
) -> list[schemas.PopularAudience]:
    """Возвращает популярные аудитории по весовой модели новой схемы событий."""
    successful_events = (
        select(Payload.event_id)
        .where(Payload.type_id == PAYLOAD_TYPE_SUCCESS_ID)
        .where(func.lower(Payload.value) == "true")
    )
    weight = case(
        (Payload.type_id == PAYLOAD_TYPE_AUDITORY_ID, 1),
        (Payload.type_id.in_([PAYLOAD_TYPE_START_ID, PAYLOAD_TYPE_END_ID]), 3),
        else_=0,
    )
    statement = (
        select(
            Payload.value.label("auditory_id"),
            func.sum(weight).label("total_weight"),
        )
        .where(
            Payload.type_id.in_(
                [
                    PAYLOAD_TYPE_AUDITORY_ID,
                    PAYLOAD_TYPE_START_ID,
                    PAYLOAD_TYPE_END_ID,
                ]
            )
        )
        .where(Payload.event_id.in_(successful_events))
        .group_by(Payload.value)
        .order_by(desc("total_weight"), Payload.value)
        .limit(limit)
    )

    rows = (await db.execute(statement)).all()
    return [
        schemas.PopularAudience(
            auditory_id=row.auditory_id,
            total_weight=int(row.total_weight or 0),
        )
        for row in rows
    ]


async def get_popular_auds(db: AsyncSession) -> list[str]:
    """Совместимый ответ для старого REST-эндпоинта популярных аудиторий."""
    return [item.auditory_id for item in await get_popular_audiences(db)]


async def get_popular_auds_with_count(db: AsyncSession) -> list[tuple[str, int]]:
    return [
        (item.auditory_id, item.total_weight)
        for item in await get_popular_audiences(db)
    ]


async def get_period_stats(
    db: AsyncSession,
    period_type: str,
    start: date | datetime,
    end: date | datetime,
    event_type_id: Optional[int] = None,
) -> list[schemas.Statistics]:
    """Группирует события по дню, месяцу или году на новой схеме событий."""
    start_dt = _as_start_datetime(start)
    end_dt = _as_end_datetime(end)
    dialect_name = db.get_bind().dialect.name
    period = _period_expression(period_type, dialect_name).label("period")
    new_client = case(
        (
            func.date(ClientId.creation_date) == func.date(Event.trigger_time),
            Event.client_id,
        ),
        else_=None,
    )

    statement = (
        select(
            period,
            func.count(Event.id).label("all_visits"),
            func.count(distinct(Event.client_id)).label("visitor_count"),
            func.count(distinct(new_client)).label("unique_visitors"),
        )
        .join(ClientId, ClientId.id == Event.client_id)
        .where(Event.trigger_time >= start_dt)
        .where(Event.trigger_time < end_dt)
        .group_by(period)
        .order_by(period)
    )
    if event_type_id is not None:
        statement = statement.where(Event.event_type_id == event_type_id)

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
    start: date | datetime,
    end: date | datetime,
    event_type_id: Optional[int] = None,
) -> schemas.AggregatedStatistics:
    """Агрегирует результат get_period_stats по выбранному периоду."""
    period_stats = await get_period_stats(db, period_type, start, end, event_type_id)
    entries = len(period_stats)
    if entries == 0:
        return _empty_aggregated_statistics()

    total_all_visits = sum(item.all_visits for item in period_stats)
    total_visitor_count = sum(item.visitor_count for item in period_stats)
    total_unique_visitors = sum(item.unique_visitors for item in period_stats)

    return schemas.AggregatedStatistics(
        total_all_visits=total_all_visits,
        total_visitor_count=total_visitor_count,
        total_unique_visitors=total_unique_visitors,
        avg_all_visits_per_day=round(total_all_visits / entries, 1),
        avg_visitor_count_per_day=round(total_visitor_count / entries, 1),
        avg_unique_visitors_per_day=round(total_unique_visitors / entries, 1),
        entries_analized=entries,
    )


def _period_from_filter(params: schemas.FilterQuery) -> tuple[str, date, date]:
    if params.start_date is not None and params.end_date is not None:
        return "day", params.start_date, params.end_date

    if params.start_month is not None and params.end_month is not None:
        start = datetime.strptime(params.start_month, "%Y-%m").date().replace(day=1)
        end_start = datetime.strptime(params.end_month, "%Y-%m").date().replace(day=1)
        if end_start.month == 12:
            end = end_start.replace(year=end_start.year + 1, month=1)
        else:
            end = end_start.replace(month=end_start.month + 1)
        return "month", start, end - timedelta(days=1)

    if params.start_year is not None and params.end_year is not None:
        start = date(int(params.start_year), 1, 1)
        end = date(int(params.end_year), 12, 31)
        return "year", start, end

    raise ValueError("Date, month or year range is required")


async def get_endpoint_stats(
    db: AsyncSession,
    params: schemas.FilterQuery,
) -> list[schemas.Statistics]:
    period_type, start, end = _period_from_filter(params)
    event_type_id = EVENT_TYPE_IDS_BY_CODE[params.target.value]
    return await get_period_stats(db, period_type, start, end, event_type_id)


async def get_agr_endp_stats(
    db: AsyncSession,
    params: schemas.FilterQuery,
) -> schemas.AggregatedStatistics:
    period_type, start, end = _period_from_filter(params)
    event_type_id = EVENT_TYPE_IDS_BY_CODE[params.target.value]
    return await get_aggregated_stats(db, period_type, start, end, event_type_id)
