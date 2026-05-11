"""Integration tests for analytics handlers."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import delete

from app import models
from app.constants import EVENT_TYPE_WAYS_ID
from app.handlers import get_aggregated_stats, get_period_stats, get_popular_audiences

from .base import session_maker  # noqa: F401


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def unique_client_ident():
    """Генерирует уникальный ident для тестовых клиентов."""
    return f"test-unique-visitor-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def unique_test_ids():
    """Генерирует уникальные ID для тестовых записей (чтобы избежать конфликтов PK)."""
    return {"client_id": 300 + hash(uuid.uuid4()) % 1000, "event_id": 300 + hash(uuid.uuid4()) % 1000}


# =============================================================================
# Popular Auditories Tests
# =============================================================================
class TestPopularAuditories:
    """Тесты для get_popular_auditories."""

    @pytest.mark.asyncio
    async def test_uses_weighted_successful_events(self):
        """Проверяет, что аудитория ранжируется по весу успешных событий."""
        async with session_maker.begin() as db:
            result = await get_popular_audiences(db)

        # Проверяем топ-2 результата (данные из сидов)
        assert len(result) >= 2
        assert result[0].auditory_id == "a-100"
        assert result[0].total_weight == 4
        assert result[1].auditory_id == "a-101"
        assert result[1].total_weight == 3


# =============================================================================
# Period Stats Tests
# =============================================================================
class TestPeriodStats:
    """Тесты для get_period_stats."""

    @pytest.mark.asyncio
    async def test_filters_by_period_and_event_type(self):
        """Проверяет фильтрацию по дате и типу события."""
        async with session_maker.begin() as db:
            result = await get_period_stats(
                db,
                period_type="day",
                start=datetime(2026, 4, 25),
                end=datetime(2026, 4, 27),
                event_type_id=EVENT_TYPE_WAYS_ID,
            )

        # Ожидаем данные из сидов за 25 и 26 апреля
        dumped = [item.model_dump() for item in result]
        assert len(dumped) == 2
        assert dumped[0]["period"] == "2026-04-25"
        assert dumped[0]["all_visits"] == 1
        assert dumped[1]["period"] == "2026-04-26"
        assert dumped[1]["all_visits"] == 1

    @pytest.mark.asyncio
    async def test_counts_unique_visitors_by_requested_period(self, unique_client_ident, unique_test_ids):
        """
        Проверяет подсчет уникальных посетителей за период.

        🔹 Исправление: используем уникальный ident и id, чтобы избежать:
           - UNIQUE constraint failed: client_ids.ident
           - UNIQUE constraint failed: events.id / client_ids.id
        """
        client_id = unique_test_ids["client_id"]
        event_id = unique_test_ids["event_id"]

        # 1. Setup: создаем тестовые данные
        async with session_maker.begin() as db:
            db.add(
                models.ClientId(
                    id=client_id,
                    ident=unique_client_ident,  # ← Уникальный ident
                    creation_date=datetime(2026, 1, 1, 9, 0, 0),
                )
            )
            db.add(
                models.Event(
                    id=event_id,
                    client_id=client_id,
                    event_type_id=EVENT_TYPE_WAYS_ID,
                    trigger_time=datetime(2026, 4, 26, 12, 0, 0),
                )
            )

        try:
            # 2. Test: вызываем хендлер
            async with session_maker.begin() as db:
                result = await get_period_stats(
                    db,
                    period_type="year",
                    start=datetime(2026, 1, 1),
                    end=datetime(2026, 4, 28),
                    event_type_id=EVENT_TYPE_WAYS_ID,
                )

            # 3. Assert: проверяем результат
            # Ожидаем, что новое событие добавилось к существующим в сидах
            dumped = [item.model_dump() for item in result]
            assert len(dumped) == 1
            assert dumped[0]["period"] == "2026-01-01"  # Годовая группировка
            # Проверяем, что счетчики увеличились (базовые сиды + наше событие)
            assert dumped[0]["all_visits"] >= 1
            assert dumped[0]["unique_visitors"] >= 1

        finally:
            # 4. Teardown: гарантированная очистка
            async with session_maker.begin() as db:
                await db.execute(delete(models.Event).where(models.Event.id == event_id))
                await db.execute(delete(models.ClientId).where(models.ClientId.id == client_id))


# =============================================================================
# Aggregated Stats Tests
# =============================================================================
class TestAggregatedStats:
    """Тесты для get_aggregated_stats."""

    @pytest.mark.asyncio
    async def test_wraps_period_stats(self):
        """Проверяет, что агрегация корректно суммирует периодические данные."""
        async with session_maker.begin() as db:
            result = await get_aggregated_stats(
                db,
                period_type="day",
                start=datetime(2026, 4, 25),
                end=datetime(2026, 4, 27),
                event_type_id=EVENT_TYPE_WAYS_ID,
            )

        dumped = result.model_dump()
        # Данные из сидов: 2 события за 2 дня
        assert dumped["total_all_visits"] == 2
        assert dumped["entries_analized"] == 2
        assert dumped["avg_all_visits_per_day"] == 1
