from datetime import date, datetime, time, timedelta
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


def _fill_missing_dates(
    stats: list[Statistics],
    start_date: date,
    end_date: date,
) -> list[Statistics]:
    stats_map = {stat.period: stat for stat in stats}
    filled_stats = []
    current_date = start_date
    while current_date <= end_date:
        period = current_date.isoformat()
        filled_stats.append(
            stats_map.get(
                period,
                Statistics(
                    period=period,
                    all_visits=0,
                    unique_visitors=0,
                    visitor_count=0,
                ),
            )
        )
        current_date += timedelta(days=1)
    return filled_stats


def _validate_month_value(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise ValueError(f"{field_name} must have format YYYY-MM") from exc


def _validate_year_value(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y")
    except ValueError as exc:
        raise ValueError(f"{field_name} must have format YYYY") from exc


def _resolve_event_type_id(endpoint: Optional[str], event_type_id: Optional[int]) -> Optional[int]:
    if endpoint is not None and event_type_id is not None:
        raise ValueError("Only one event type filter can be provided")
    if event_type_id is not None:
        return event_type_id
    if endpoint is None:
        return None
    if endpoint not in EVENT_TYPE_IDS_BY_CODE:
        raise ValueError(f"Unknown endpoint/event type code: {endpoint}")
    return EVENT_TYPE_IDS_BY_CODE[endpoint]


def _resolve_window(
    by_date: Optional[EndpointStatisticsByDateInput],
    by_month: Optional[EndpointStatisticsByMonthInput],
    by_year: Optional[EndpointStatisticsByYearInput],
) -> tuple[str, datetime, datetime, Optional[date], Optional[date]]:
    active_filters_count = sum(item is not None for item in (by_date, by_month, by_year))
    if active_filters_count != 1:
        raise ValueError("Exactly one filter must be provided: by_date, by_month, or by_year")

    if by_date is not None:
        if by_date.start > by_date.end:
            raise ValueError("by_date.start must be less than or equal to by_date.end")
        today = date.today()
        effective_end = min(by_date.end, today)
        if by_date.start > effective_end:
            raise ValueError("by_date.start must not be greater than today's date")
        return (
            "day",
            datetime.combine(by_date.start, time.min),
            datetime.combine(effective_end + timedelta(days=1), time.min),
            by_date.start,
            effective_end,
        )

    if by_month is not None:
        _validate_month_value(by_month.start, "by_month.start")
        _validate_month_value(by_month.end, "by_month.end")
        if by_month.start > by_month.end:
            raise ValueError("by_month.start must be less than or equal to by_month.end")
        start = datetime.strptime(by_month.start, "%Y-%m")
        end_month = datetime.strptime(by_month.end, "%Y-%m")
        end = datetime(end_month.year + (end_month.month == 12), end_month.month % 12 + 1, 1)
        return "month", start, end, None, None

    if by_year is None:
        raise ValueError("One filter must be provided")
    _validate_year_value(by_year.start, "by_year.start")
    _validate_year_value(by_year.end, "by_year.end")
    if by_year.start > by_year.end:
        raise ValueError("by_year.start must be less than or equal to by_year.end")
    return (
        "year",
        datetime.strptime(by_year.start, "%Y"),
        datetime(int(by_year.end) + 1, 1, 1),
        None,
        None,
    )


async def resolve_endpoint_statistics(
    info: Info,
    endpoint: Optional[str] = None,
    event_type_id: Optional[int] = None,
    by_date: Optional[EndpointStatisticsByDateInput] = None,
    by_month: Optional[EndpointStatisticsByMonthInput] = None,
    by_year: Optional[EndpointStatisticsByYearInput] = None,
) -> list[EndpointStatisticsType]:
    session = await ensure_stats_view_permission(info)
    period_type, start, end, fill_start, fill_end = _resolve_window(by_date, by_month, by_year)
    stats = await get_period_stats(
        session,
        period_type=period_type,
        start=start,
        end=end,
        event_type_id=_resolve_event_type_id(endpoint, event_type_id),
    )
    if fill_start is not None and fill_end is not None:
        stats = _fill_missing_dates(stats, fill_start, fill_end)
    return [_to_endpoint_statistics(stat) for stat in stats]


@strawberry.type
class AggregatedEndpointStatisticsType:
    total_visits: int
    total_unique: int
    total_visitor_count: int
    avg_visits: float
    avg_unique: float
    avg_visitor_count: float
    entries_count: int


def _to_aggregated_endpoint_statistics(
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
    period_type, start, end, _, _ = _resolve_window(by_date, by_month, by_year)
    aggregated_stats = await get_aggregated_stats(
        session,
        period_type=period_type,
        start=start,
        end=end,
        event_type_id=_resolve_event_type_id(endpoint, event_type_id),
    )
    return _to_aggregated_endpoint_statistics(aggregated_stats)
