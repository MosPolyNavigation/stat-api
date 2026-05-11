from datetime import date, datetime, time, timedelta
from typing import Optional, List
import strawberry
from strawberry import Info

from app.constants import EVENT_TYPE_IDS_BY_CODE
from app.graphql.core.context import GraphQLContext
from app.graphql.core.permissions import require_permissions, P
from app.handlers import get_aggregated_stats, get_period_stats

from app.graphql.domains.stat.inputs import (
    EndpointStatisticsByDateInput,
    EndpointStatisticsByMonthInput,
    EndpointStatisticsByYearInput,
)
from app.graphql.domains.stat.types import (
    EndpointStatistics,
    AggregatedEndpointStatistics,
    _to_endpoint_statistics,
    _to_aggregated_endpoint_statistics,
    _fill_missing_dates,
)


# =============================================================================
# Валидация и резолвинг параметров окна
# =============================================================================
def _validate_month_value(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise ValueError(f"{field_name} должен быть в формате YYYY-MM") from exc


def _validate_year_value(value: str, field_name: str) -> None:
    try:
        datetime.strptime(value, "%Y")
    except ValueError as exc:
        raise ValueError(f"{field_name} должен быть в формате YYYY") from exc


def _resolve_event_type_id(endpoint: Optional[str], event_type_id: Optional[int]) -> Optional[int]:
    if endpoint is not None and event_type_id is not None:
        raise ValueError("Можно передать только один фильтр типа события")
    if event_type_id is not None:
        return event_type_id
    if endpoint is None:
        return None
    if endpoint not in EVENT_TYPE_IDS_BY_CODE:
        raise ValueError(f"Неизвестный код endpoint/event type: {endpoint}")
    return EVENT_TYPE_IDS_BY_CODE[endpoint]


def _resolve_window(
        by_date: Optional[EndpointStatisticsByDateInput],
        by_month: Optional[EndpointStatisticsByMonthInput],
        by_year: Optional[EndpointStatisticsByYearInput],
) -> tuple[str, datetime, datetime, Optional[date], Optional[date]]:
    active_filters_count = sum(item is not None for item in (by_date, by_month, by_year))
    if active_filters_count != 1:
        raise ValueError("Нужно передать ровно один фильтр: by_date, by_month или by_year")

    if by_date is not None:
        if by_date.start > by_date.end:
            raise ValueError("by_date.start должен быть меньше или равен by_date.end")
        today = date.today()
        effective_end = min(by_date.end, today)
        if by_date.start > effective_end:
            raise ValueError("by_date.start не должен быть больше сегодняшней даты")
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
            raise ValueError("by_month.start должен быть меньше или равен by_month.end")
        start = datetime.strptime(by_month.start, "%Y-%m")
        end_month = datetime.strptime(by_month.end, "%Y-%m")
        end = datetime(end_month.year + (end_month.month == 12), end_month.month % 12 + 1, 1)
        return "month", start, end, None, None

    if by_year is None:
        raise ValueError("Нужно передать один фильтр")
    _validate_year_value(by_year.start, "by_year.start")
    _validate_year_value(by_year.end, "by_year.end")
    if by_year.start > by_year.end:
        raise ValueError("by_year.start должен быть меньше или равен by_year.end")
    return (
        "year",
        datetime.strptime(by_year.start, "%Y"),
        datetime(int(by_year.end) + 1, 1, 1),
        None,
        None,
    )


# =============================================================================
# Query Type
# =============================================================================
@strawberry.type
class StatisticsQuery:
    @strawberry.field  # type: ignore[unresolved-reference]
    async def endpoint_statistics(
            self,
            info: Info,
            endpoint: Optional[str] = None,
            event_type_id: Optional[int] = None,
            by_date: Optional[EndpointStatisticsByDateInput] = None,
            by_month: Optional[EndpointStatisticsByMonthInput] = None,
            by_year: Optional[EndpointStatisticsByYearInput] = None,
    ) -> List[EndpointStatistics]:
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context
        period_type, start, end, fill_start, fill_end = _resolve_window(by_date, by_month, by_year)

        stats = await get_period_stats(
            ctx.db,
            period_type=period_type,
            start=start,
            end=end,
            event_type_id=_resolve_event_type_id(endpoint, event_type_id),
        )

        if fill_start is not None and fill_end is not None:
            stats = _fill_missing_dates(stats, fill_start, fill_end)

        return [_to_endpoint_statistics(stat) for stat in stats]

    @strawberry.field  # type: ignore[unresolved-reference]
    async def endpoint_statistics_avg(
            self,
            info: Info,
            endpoint: Optional[str] = None,
            event_type_id: Optional[int] = None,
            by_date: Optional[EndpointStatisticsByDateInput] = None,
            by_month: Optional[EndpointStatisticsByMonthInput] = None,
            by_year: Optional[EndpointStatisticsByYearInput] = None,
    ) -> AggregatedEndpointStatistics:
        await require_permissions(info, P.STATS_VIEW)
        ctx: GraphQLContext = info.context
        period_type, start, end, _, _ = _resolve_window(by_date, by_month, by_year)

        aggregated_stats = await get_aggregated_stats(
            ctx.db,
            period_type=period_type,
            start=start,
            end=end,
            event_type_id=_resolve_event_type_id(endpoint, event_type_id),
        )

        return _to_aggregated_endpoint_statistics(aggregated_stats)
