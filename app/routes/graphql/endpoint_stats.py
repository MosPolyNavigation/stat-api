from datetime import date, datetime
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


async def resolve_endpoint_statistics(
    info: Info,
    endpoint: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list[EndpointStatisticsType]:
    session: Session = info.context["db"]
    params = FilterQuery(
        target=TargetEnum(endpoint),
        start_date=start_date.date() if start_date else None,
        end_date=end_date.date() if end_date else None
    )
    stats = await get_endpoint_stats(session, params)
    return [_to_endpoint_statistics(stat) for stat in stats]
