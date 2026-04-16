from datetime import date, datetime, timedelta
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info
from typing import Optional
from .permissions import ensure_stats_view_permission
from app.handlers import get_agr_endp_stats_stub, get_endpoint_stats_stub
from app.schemas import Statistics, AggregatedStatistics, FilterQuery
from app.schemas.filter import TargetEnum


@strawberry.type
class EndpointStatisticsType:
    unique_visitors: int
    all_visits: int
    visitor_count: int
    period: date


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
        stats: list[Statistics], start_date: date, end_date: date
) -> list[Statistics]:
    stats_map = {stat.period: stat for stat in stats}
    filled_stats = []
    current_date = start_date
    end_date += timedelta(days=1)
    while current_date < end_date:
        if current_date in stats_map:
            filled_stats.append(stats_map[current_date])
        else:
            filled_stats.append(
                Statistics(
                    period=current_date,
                    all_visits=0,
                    unique_visitors=0,
                    visitor_count=0
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


async def resolve_endpoint_statistics(
        info: Info,
        endpoint: str,
        by_date: Optional[EndpointStatisticsByDateInput] = None,
        by_month: Optional[EndpointStatisticsByMonthInput] = None,
        by_year: Optional[EndpointStatisticsByYearInput] = None,
) -> list[EndpointStatisticsType]:
    active_filters_count = sum(
        item is not None for item in (by_date, by_month, by_year)
    )
    if active_filters_count != 1:
        raise ValueError(
            "Exactly one filter must be provided: by_date, by_month, or by_year"
        )

    effective_start_date: Optional[date] = None
    effective_end_date: Optional[date] = None
    effective_start_month: Optional[str] = None
    effective_end_month: Optional[str] = None
    effective_start_year: Optional[str] = None
    effective_end_year: Optional[str] = None
    today = date.today()

    if by_date is not None:
        if by_date.start > by_date.end:
            raise ValueError("by_date.start must be less than or equal to by_date.end")
        effective_start_date = by_date.start
        effective_end_date = min(by_date.end, today)
        if effective_start_date > effective_end_date:
            raise ValueError("by_date.start must not be greater than today's date")
    elif by_month is not None:
        _validate_month_value(by_month.start, "by_month.start")
        _validate_month_value(by_month.end, "by_month.end")
        if by_month.start > by_month.end:
            raise ValueError("by_month.start must be less than or equal to by_month.end")
        effective_start_month = by_month.start
        effective_end_month = by_month.end
    elif by_year is not None:
        _validate_year_value(by_year.start, "by_year.start")
        _validate_year_value(by_year.end, "by_year.end")
        if by_year.start > by_year.end:
            raise ValueError("by_year.start must be less than or equal to by_year.end")
        effective_start_year = by_year.start
        effective_end_year = by_year.end

    session: AsyncSession = await ensure_stats_view_permission(info)
    params = FilterQuery(
        target=TargetEnum(endpoint),
        start_date=effective_start_date,
        end_date=effective_end_date,
        start_month=effective_start_month,
        end_month=effective_end_month,
        start_year=effective_start_year,
        end_year=effective_end_year,
    )
    # TODO: restore after analytics refactor
    stats = await get_endpoint_stats_stub(session, params)
    if by_date is not None and effective_start_date is not None and effective_end_date is not None:
        stats = _fill_missing_dates(stats, effective_start_date, effective_end_date)
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


def _to_aggregated_endpoint_statistics(model: AggregatedStatistics) -> AggregatedEndpointStatisticsType:
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
        endpoint: str,
        by_date: Optional[EndpointStatisticsByDateInput] = None,
        by_month: Optional[EndpointStatisticsByMonthInput] = None,
        by_year: Optional[EndpointStatisticsByYearInput] = None,
) -> AggregatedEndpointStatisticsType:
    active_filters_count = sum(
        item is not None for item in (by_date, by_month, by_year)
    )
    if active_filters_count != 1:
        raise ValueError(
            "Exactly one filter must be provided: by_date, by_month, or by_year"
        )

    effective_start_date: Optional[date] = None
    effective_end_date: Optional[date] = None
    effective_start_month: Optional[str] = None
    effective_end_month: Optional[str] = None
    effective_start_year: Optional[str] = None
    effective_end_year: Optional[str] = None
    today = date.today()

    if by_date is not None:
        if by_date.start > by_date.end:
            raise ValueError("by_date.start must be less than or equal to by_date.end")
        effective_start_date = by_date.start
        effective_end_date = min(by_date.end, today)
        if effective_start_date > effective_end_date:
            raise ValueError("by_date.start must not be greater than today's date")
    elif by_month is not None:
        _validate_month_value(by_month.start, "by_month.start")
        _validate_month_value(by_month.end, "by_month.end")
        if by_month.start > by_month.end:
            raise ValueError("by_month.start must be less than or equal to by_month.end")
        effective_start_month = by_month.start
        effective_end_month = by_month.end
    elif by_year is not None:
        _validate_year_value(by_year.start, "by_year.start")
        _validate_year_value(by_year.end, "by_year.end")
        if by_year.start > by_year.end:
            raise ValueError("by_year.start must be less than or equal to by_year.end")
        effective_start_year = by_year.start
        effective_end_year = by_year.end

    session: AsyncSession = await ensure_stats_view_permission(info)
    params = FilterQuery(
        target=TargetEnum(endpoint),
        start_date=effective_start_date,
        end_date=effective_end_date,
        start_month=effective_start_month,
        end_month=effective_end_month,
        start_year=effective_start_year,
        end_year=effective_end_year,
    )
    # TODO: restore after analytics refactor
    aggregated_stats = await get_agr_endp_stats_stub(session, params)
    return _to_aggregated_endpoint_statistics(aggregated_stats)
