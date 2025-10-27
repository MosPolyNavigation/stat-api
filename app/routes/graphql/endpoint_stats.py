from datetime import date, timedelta
import strawberry
from sqlalchemy.orm import Session
from strawberry import Info
from typing import Optional
from app.handlers import get_endpoint_stats
from app.schemas import Statistics, FilterQuery
from app.schemas.filter import TargetEnum


@strawberry.type
class EndpointStatisticsType:
    unique_visitors: int
    all_visits: int
    visitor_count: int
    period: date


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


async def resolve_endpoint_statistics(
        info: Info,
        endpoint: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
) -> list[EndpointStatisticsType]:
    today_plus_one = date.today()
    effective_end_date = None
    effective_start_date = start_date
    if end_date is not None:
        effective_end_date = min(end_date, today_plus_one)

    session: Session = info.context["db"]
    params = FilterQuery(
        target=TargetEnum(endpoint),
        start_date=effective_start_date,
        end_date=effective_end_date
    )
    stats = await get_endpoint_stats(session, params)
    if effective_start_date is not None and effective_end_date is not None:
        stats = _fill_missing_dates(stats, effective_start_date, effective_end_date)
    return [_to_endpoint_statistics(stat) for stat in stats]
