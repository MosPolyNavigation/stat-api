from datetime import date, datetime, timedelta
from typing import Optional

import strawberry
from strawberry import Info

from app.constants import EVENT_TYPE_IDS_BY_CODE
from app.handlers import get_aggregated_stats, get_period_stats
from app.schemas import AggregatedStatistics, Statistics

from .permissions import ensure_stats_view_permission


@strawberry.type
class EndpointStatisticsType:
    unique_visitors: int
    all_visits: int
    visitor_count: int
    period: str


@strawberry.input
class EndpointStatisticsByDateInput:
    start: date
    end: date


@strawberry.input
class EndpointStatisticsByMonthInput:
    start: str
    end: str


@strawberry.input
class EndpointStatisticsByYearInput:
    start: str
    end: str


def _to_endpoint_statistics(model: Statistics) -> EndpointStatisticsType:
    return EndpointStatisticsType(
        unique_visitors=model.unique_visitors,
        visitor_count=model.visitor_count,
        all_visits=model.all_visits,
        period=model.period,
    )


def _validate_month_value(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise ValueError(f"{field_name} must have format YYYY-MM") from exc


def _validate_year_value(value: str, field_name: str) -> None:
    if len(value) != 4 or not value.isdigit():
        raise ValueError(f"{field_name} must have format YYYY")


def _add_month(value: date) -> date:
    if value.month == 12:
        return value.replace(year=value.year + 1, month=1)
    return value.replace(month=value.month + 1)


def _fill_missing_periods(
    stats: list[Statistics],
    period_type: str,
    start: date,
    end: date,
) -> list[Statistics]:
    stats_map = {item.period: item for item in stats}
    filled_stats: list[Statistics] = []

    if period_type == "day":
        current = start
        while current <= end:
            key = current.isoformat()
            filled_stats.append(
                stats_map.get(
                    key,
                    Statistics(
                        period=key,
                        all_visits=0,
                        unique_visitors=0,
                        visitor_count=0,
                    ),
                )
            )
            current += timedelta(days=1)
        return filled_stats

    if period_type == "month":
        current = start.replace(day=1)
        end_month = end.replace(day=1)
        while current <= end_month:
            key = current.strftime("%Y-%m")
            filled_stats.append(
                stats_map.get(
                    key,
                    Statistics(
                        period=key,
                        all_visits=0,
                        unique_visitors=0,
                        visitor_count=0,
                    ),
                )
            )
            current = _add_month(current)
        return filled_stats

    current_year = start.year
    while current_year <= end.year:
        key = str(current_year)
        filled_stats.append(
            stats_map.get(
                key,
                Statistics(
                    period=key,
                    all_visits=0,
                    unique_visitors=0,
                    visitor_count=0,
                ),
            )
        )
        current_year += 1
    return filled_stats


def _resolve_event_type_id(
    endpoint: Optional[str],
    event_type_id: Optional[int],
) -> Optional[int]:
    if event_type_id is not None:
        return event_type_id
    if endpoint is None:
        return None
    try:
        return EVENT_TYPE_IDS_BY_CODE[endpoint]
    except KeyError as exc:
        raise ValueError("Unknown event endpoint") from exc


def _resolve_period(
    by_date: Optional[EndpointStatisticsByDateInput],
    by_month: Optional[EndpointStatisticsByMonthInput],
    by_year: Optional[EndpointStatisticsByYearInput],
) -> tuple[str, date, date]:
    active_filters_count = sum(
        item is not None for item in (by_date, by_month, by_year)
    )
    if active_filters_count != 1:
        raise ValueError("Exactly one date filter must be provided")

    if by_date is not None:
        if by_date.start > by_date.end:
            raise ValueError("by_date.start must be less than or equal to by_date.end")
        return "day", by_date.start, by_date.end

    if by_month is not None:
        _validate_month_value(by_month.start, "by_month.start")
        _validate_month_value(by_month.end, "by_month.end")
        start = datetime.strptime(by_month.start, "%Y-%m").date().replace(day=1)
        end = datetime.strptime(by_month.end, "%Y-%m").date().replace(day=1)
        if start > end:
            raise ValueError("by_month.start must be less than or equal to by_month.end")
        return "month", start, _add_month(end) - timedelta(days=1)

    if by_year is None:
        raise ValueError("Date filter is required")
    _validate_year_value(by_year.start, "by_year.start")
    _validate_year_value(by_year.end, "by_year.end")
    start_year = int(by_year.start)
    end_year = int(by_year.end)
    if start_year > end_year:
        raise ValueError("by_year.start must be less than or equal to by_year.end")
    return "year", date(start_year, 1, 1), date(end_year, 12, 31)


async def resolve_endpoint_statistics(
    info: Info,
    endpoint: Optional[str] = None,
    event_type_id: Optional[int] = None,
    by_date: Optional[EndpointStatisticsByDateInput] = None,
    by_month: Optional[EndpointStatisticsByMonthInput] = None,
    by_year: Optional[EndpointStatisticsByYearInput] = None,
) -> list[EndpointStatisticsType]:
    session = await ensure_stats_view_permission(info)
    effective_event_type_id = _resolve_event_type_id(endpoint, event_type_id)
    period_type, start, end = _resolve_period(by_date, by_month, by_year)
    stats = await get_period_stats(
        session,
        period_type,
        start,
        end,
        effective_event_type_id,
    )
    return [
        _to_endpoint_statistics(item)
        for item in _fill_missing_periods(stats, period_type, start, end)
    ]


@strawberry.type
class AggregatedEndpointStatisticsType:
    total_visits: int
    total_unique: int
    total_visitor_count: int
    avg_visits: float
    avg_unique: float
    avg_visitor_count: float
    entries_count: int


def _to_aggregated_statistics(
    model: AggregatedStatistics,
) -> AggregatedEndpointStatisticsType:
    return AggregatedEndpointStatisticsType(
        total_visits=model.total_all_visits,
        total_unique=model.total_unique_visitors,
        total_visitor_count=model.total_visitor_count,
        avg_visits=model.avg_all_visits_per_day,
        avg_unique=model.avg_unique_visitors_per_day,
        avg_visitor_count=model.avg_visitor_count_per_day,
        entries_count=model.entries_analized,
    )


async def resolve_endpoint_statistics_avg(
    info: Info,
    endpoint: Optional[str] = None,
    event_type_id: Optional[int] = None,
    by_date: Optional[EndpointStatisticsByDateInput] = None,
    by_month: Optional[EndpointStatisticsByMonthInput] = None,
    by_year: Optional[EndpointStatisticsByYearInput] = None,
) -> AggregatedEndpointStatisticsType:
    session = await ensure_stats_view_permission(info)
    effective_event_type_id = _resolve_event_type_id(endpoint, event_type_id)
    period_type, start, end = _resolve_period(by_date, by_month, by_year)
    stats = await get_aggregated_stats(
        session,
        period_type,
        start,
        end,
        effective_event_type_id,
    )
    return _to_aggregated_statistics(stats)
