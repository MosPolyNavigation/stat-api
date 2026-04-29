import asyncio
from datetime import datetime

from app.constants import EVENT_TYPE_WAYS_ID
from app.database import AsyncSessionLocal
from app.handlers import get_aggregated_stats, get_period_stats, get_popular_audiences

from .base import client  # noqa: F401


def test_popular_audiences_uses_weighted_successful_events():
    async def run():
        async with AsyncSessionLocal() as db:
            return await get_popular_audiences(db)

    result = asyncio.run(run())

    assert [item.model_dump() for item in result[:2]] == [
        {"auditory_id": "a-100", "total_weight": 4},
        {"auditory_id": "a-101", "total_weight": 3},
    ]


def test_period_stats_filters_by_period_and_event_type():
    async def run():
        async with AsyncSessionLocal() as db:
            return await get_period_stats(
                db,
                period_type="day",
                start=datetime(2026, 4, 25),
                end=datetime(2026, 4, 27),
                event_type_id=EVENT_TYPE_WAYS_ID,
            )

    result = asyncio.run(run())

    assert [item.model_dump() for item in result] == [
        {
            "period": "2026-04-25",
            "all_visits": 1,
            "visitor_count": 1,
            "unique_visitors": 1,
        },
        {
            "period": "2026-04-26",
            "all_visits": 1,
            "visitor_count": 1,
            "unique_visitors": 1,
        },
    ]


def test_aggregated_stats_wraps_period_stats():
    async def run():
        async with AsyncSessionLocal() as db:
            return await get_aggregated_stats(
                db,
                period_type="day",
                start=datetime(2026, 4, 25),
                end=datetime(2026, 4, 27),
                event_type_id=EVENT_TYPE_WAYS_ID,
            )

    result = asyncio.run(run())

    assert result.model_dump() == {
        "total_all_visits": 2,
        "total_unique_visitors": 2,
        "total_visitor_count": 2,
        "avg_all_visits_per_day": 1.0,
        "avg_unique_visitors_per_day": 1.0,
        "avg_visitor_count_per_day": 1.0,
        "entries_analized": 2,
    }
