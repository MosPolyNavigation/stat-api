from datetime import date, timedelta
from typing import List
import strawberry
from app.schemas import Statistics, AggregatedStatistics


# =============================================================================
# Хелперы конвертации и заполнения дат
# =============================================================================
def _to_endpoint_statistics(model: Statistics) -> "EndpointStatistics":
    return EndpointStatistics(
        unique_visitors=model.unique_visitors,
        visitor_count=model.visitor_count,
        all_visits=model.all_visits,
        period=model.period,
    )


def _to_aggregated_endpoint_statistics(
    model: AggregatedStatistics,
) -> "AggregatedEndpointStatistics":
    return AggregatedEndpointStatistics(
        total_visits=model.total_all_visits,
        total_unique=model.total_unique_visitors,
        total_visitor_count=model.total_visitor_count,
        avg_visits=model.avg_all_visits_per_day,
        avg_unique=model.avg_unique_visitors_per_day,
        avg_visitor_count=model.avg_visitor_count_per_day,
        entries_count=model.entries_analized,
    )


def _fill_missing_dates(
    stats: List[Statistics], start_date: date, end_date: date
) -> List[Statistics]:
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


# =============================================================================
# Типы для статистики эндпоинтов
# =============================================================================
@strawberry.type
class EndpointStatistics:
    unique_visitors: int
    all_visits: int
    visitor_count: int
    period: str


@strawberry.type
class AggregatedEndpointStatistics:
    total_visits: int
    total_unique: int
    total_visitor_count: int
    avg_visits: float
    avg_unique: float
    avg_visitor_count: float
    entries_count: int
