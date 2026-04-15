from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas


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


async def get_endpoint_stats_stub(
    db: AsyncSession,
    params: schemas.FilterQuery,
) -> list[schemas.Statistics]:
    _ = (db, params)
    return []


async def get_agr_endp_stats_stub(
    db: AsyncSession,
    params: schemas.FilterQuery,
) -> schemas.AggregatedStatistics:
    _ = (db, params)
    return _empty_aggregated_statistics()


async def get_popular_auds_stub(db: AsyncSession) -> list[str]:
    _ = db
    return []


async def get_popular_auds_with_count_stub(
    db: AsyncSession,
) -> list[tuple[str, int]]:
    _ = db
    return []


async def get_tg_stats_stub(
    db: AsyncSession,
    params: schemas.TgFilterQuery,
) -> list[schemas.Statistics]:
    _ = (db, params)
    return []


async def get_agr_tg_stats_stub(
    db: AsyncSession,
    params: schemas.TgFilterQuery,
) -> schemas.AggregatedStatistics:
    _ = (db, params)
    return _empty_aggregated_statistics()
