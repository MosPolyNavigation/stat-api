import asyncio
from datetime import date, datetime

from app import models
from app.constants import EVENT_TYPE_AUDS_ID, EVENT_TYPE_WAYS_ID
from app.database import AsyncSessionLocal
from app.handlers import (
    get_aggregated_stats,
    get_period_stats,
    get_popular_audiences,
)
from .base import client  # noqa: F401 - инициализирует тестовую БД


def _run(coro):
    return asyncio.run(coro)


def test_popular_audiences_weight_system():
    async def case():
        async with AsyncSessionLocal.begin() as db:
            aud_event = models.Event(
                client_id=1,
                event_type_id=EVENT_TYPE_AUDS_ID,
                trigger_time=datetime(2025, 1, 3, 10, 0, 0),
            )
            way_event = models.Event(
                client_id=1,
                event_type_id=EVENT_TYPE_WAYS_ID,
                trigger_time=datetime(2025, 1, 3, 11, 0, 0),
            )
            failed_aud_event = models.Event(
                client_id=1,
                event_type_id=EVENT_TYPE_AUDS_ID,
                trigger_time=datetime(2025, 1, 3, 12, 0, 0),
            )
            db.add_all([aud_event, way_event, failed_aud_event])
            await db.flush()
            db.add_all([
                models.Payload(event=aud_event, type_id=2, value="test-weight-a"),
                models.Payload(event=aud_event, type_id=5, value="true"),
                models.Payload(event=way_event, type_id=3, value="test-weight-a"),
                models.Payload(event=way_event, type_id=4, value="test-weight-b"),
                models.Payload(event=way_event, type_id=5, value="true"),
                models.Payload(event=failed_aud_event, type_id=2, value="test-weight-c"),
                models.Payload(event=failed_aud_event, type_id=5, value="false"),
            ])

        async with AsyncSessionLocal() as db:
            return await get_popular_audiences(db)

    result = _run(case())
    weights = {item.auditory_id: item.total_weight for item in result}

    assert weights["test-weight-a"] == 4
    assert weights["test-weight-b"] == 3
    assert "test-weight-c" not in weights


def test_period_stats_filters_by_day_and_event_type():
    async def case():
        async with AsyncSessionLocal() as db:
            return await get_period_stats(
                db,
                "day",
                date(2025, 1, 1),
                date(2025, 1, 2),
                EVENT_TYPE_AUDS_ID,
            )

    result = _run(case())

    assert len(result) == 1
    assert result[0].period == "2025-01-01"
    assert result[0].all_visits == 1
    assert result[0].visitor_count == 1
    assert result[0].unique_visitors == 1


def test_aggregated_stats_sums_period_stats():
    async def case():
        async with AsyncSessionLocal() as db:
            return await get_aggregated_stats(
                db,
                "day",
                date(2025, 1, 1),
                date(2025, 1, 2),
            )

    result = _run(case())

    assert result.total_all_visits == 4
    assert result.total_visitor_count == 2
    assert result.total_unique_visitors == 2
    assert result.avg_all_visits_per_day == 2.0
    assert result.entries_analized == 2
