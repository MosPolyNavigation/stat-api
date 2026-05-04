import asyncio
from datetime import datetime

from sqlalchemy import delete

from app import models
from app.constants import EVENT_TYPE_WAYS_ID
from app.handlers import get_aggregated_stats, get_period_stats, get_popular_audiences

from .base import client, test_session_maker  # noqa: F401


def test_popular_audiences_uses_weighted_successful_events():
    async def run():
        async with test_session_maker.begin() as db:
            return await get_popular_audiences(db)

    result = asyncio.run(run())

    assert [item.model_dump() for item in result[:2]] == [
        {"auditory_id": "a-100", "total_weight": 4},
        {"auditory_id": "a-101", "total_weight": 3},
    ]


def test_period_stats_filters_by_period_and_event_type():
    async def run():
        async with test_session_maker.begin() as db:
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


def test_period_stats_counts_unique_visitors_by_requested_period():
    async def run():
        async with test_session_maker.begin() as db:
            db.add(
                models.ClientId(
                    id=300,
                    ident="33e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
                    creation_date=datetime(2026, 1, 1, 9, 0, 0),
                )
            )
            db.add(
                models.Event(
                    id=300,
                    client_id=300,
                    event_type_id=EVENT_TYPE_WAYS_ID,
                    trigger_time=datetime(2026, 4, 26, 12, 0, 0),
                )
            )
        try:
            async with test_session_maker.begin() as db:
                return await get_period_stats(
                    db,
                    period_type="year",
                    start=datetime(2026, 1, 1),
                    end=datetime(2027, 1, 1),
                    event_type_id=EVENT_TYPE_WAYS_ID,
                )
        finally:
            async with test_session_maker.begin() as db:
                await db.execute(delete(models.Event).where(models.Event.id == 300))
                await db.execute(delete(models.ClientId).where(models.ClientId.id == 300))

    result = asyncio.run(run())

    assert [item.model_dump() for item in result] == [
        {
            "period": "2026-01-01",
            "all_visits": 3,
            "visitor_count": 3,
            "unique_visitors": 3,
        },
    ]


def test_aggregated_stats_wraps_period_stats():
    async def run():
        async with test_session_maker.begin() as db:
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


def test_aggregated_stats_counts_global_visitors_once():
    async def run():
        async with test_session_maker.begin() as db:
            db.add(
                models.Event(
                    id=200,
                    client_id=1,
                    event_type_id=EVENT_TYPE_WAYS_ID,
                    trigger_time=datetime(2026, 4, 26, 12, 0, 0),
                )
            )
        try:
            async with test_session_maker.begin() as db:
                return await get_aggregated_stats(
                    db,
                    period_type="day",
                    start=datetime(2026, 4, 25),
                    end=datetime(2026, 4, 27),
                    event_type_id=EVENT_TYPE_WAYS_ID,
                )
        finally:
            async with test_session_maker.begin() as db:
                await db.execute(delete(models.Event).where(models.Event.id == 200))

    result = asyncio.run(run())

    assert result.model_dump() == {
        "total_all_visits": 3,
        "total_unique_visitors": 2,
        "total_visitor_count": 2,
        "avg_all_visits_per_day": 1.5,
        "avg_unique_visitors_per_day": 1.0,
        "avg_visitor_count_per_day": 1.5,
        "entries_analized": 2,
    }
