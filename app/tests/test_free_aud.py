"""Тесты для эндпоинтов поиска свободных аудиторий /api/free-aud"""

import pytest
from .base import client
import app.globals as globals_


class TestFreeAudByAud:
    """Тесты для GET /api/free-aud/by-aud - поиск свободной аудитории по ID"""

    def test_200_free_aud_by_aud_success(self):
        """Успешный поиск свободной аудитории по ID"""
        response = client.get(
            "/api/free-aud/by-aud",
            params={
                "aud_id": "test-101",
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Проверяем, что ответ содержит информацию об аудитории
        assert isinstance(data, dict)

    def test_200_free_aud_by_aud_with_day(self):
        """Поиск свободной аудитории с фильтром по дню недели"""
        response = client.get(
            "/api/free-aud/by-aud",
            params={
                "aud_id": "test-101",
                "start_date": "2025-02-01",
                "day": "monday"
            }
        )
        assert response.status_code == 200

    def test_200_free_aud_by_aud_with_para(self):
        """Поиск свободной аудитории с фильтром по номеру пары"""
        response = client.get(
            "/api/free-aud/by-aud",
            params={
                "aud_id": "test-101",
                "start_date": "2025-02-01",
                "para": "1"
            }
        )
        assert response.status_code == 200

    def test_200_free_aud_by_aud_with_date_range(self):
        """Поиск свободной аудитории с диапазоном дат"""
        response = client.get(
            "/api/free-aud/by-aud",
            params={
                "aud_id": "test-101",
                "start_date": "2025-02-01",
                "end_date": "2025-06-30"
            }
        )
        assert response.status_code == 200

    def test_200_free_aud_by_aud_all_filters(self):
        """Поиск с использованием всех фильтров одновременно"""
        response = client.get(
            "/api/free-aud/by-aud",
            params={
                "aud_id": "test-101",
                "start_date": "2025-02-01",
                "end_date": "2025-06-30",
                "day": "wednesday",
                "para": "3"
            }
        )
        assert response.status_code == 200

    def test_422_free_aud_by_aud_missing_aud_id(self):
        """Ошибка валидации при отсутствии aud_id"""
        response = client.get(
            "/api/free-aud/by-aud",
            params={
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 422

    def test_422_free_aud_by_aud_missing_start_date(self):
        """Ошибка валидации при отсутствии start_date"""
        response = client.get(
            "/api/free-aud/by-aud",
            params={
                "aud_id": "test-101"
            }
        )
        assert response.status_code == 422

    def test_425_free_aud_by_aud_schedule_not_loaded(self):
        """Тест для проверки статуса 425 когда расписание не загружено"""
        # Сохраняем текущее состояние
        original_locker = globals_.locker

        try:
            # Устанавливаем locker=True для имитации загрузки расписания
            globals_.locker = True

            response = client.get(
                "/api/free-aud/by-aud",
                params={
                    "aud_id": "test-101",
                    "start_date": "2025-02-01"
                }
            )
            assert response.status_code == 425
            data = response.json()
            assert "status" in data
            assert "not loaded" in data["status"].lower()
        finally:
            # Восстанавливаем состояние
            globals_.locker = original_locker


class TestFreeAudByPlan:
    """Тесты для GET /api/free-aud/by-plan - поиск свободных аудиторий по плану"""

    def test_200_free_aud_by_plan_success(self):
        """Успешный поиск свободных аудиторий по плану"""
        response = client.get(
            "/api/free-aud/by-plan",
            params={
                "plan_id": "test-plan-1",
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_200_free_aud_by_plan_with_filters(self):
        """Поиск свободных аудиторий по плану с фильтрами"""
        response = client.get(
            "/api/free-aud/by-plan",
            params={
                "plan_id": "test-plan-1",
                "start_date": "2025-02-01",
                "end_date": "2025-06-30",
                "day": "friday",
                "para": "2"
            }
        )
        assert response.status_code == 200

    def test_422_free_aud_by_plan_missing_plan_id(self):
        """Ошибка валидации при отсутствии plan_id"""
        response = client.get(
            "/api/free-aud/by-plan",
            params={
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 422

    def test_422_free_aud_by_plan_missing_start_date(self):
        """Ошибка валидации при отсутствии start_date"""
        response = client.get(
            "/api/free-aud/by-plan",
            params={
                "plan_id": "test-plan-1"
            }
        )
        assert response.status_code == 422

    def test_425_free_aud_by_plan_schedule_not_loaded(self):
        """Тест для проверки статуса 425 когда расписание не загружено"""
        original_locker = globals_.locker

        try:
            globals_.locker = True

            response = client.get(
                "/api/free-aud/by-plan",
                params={
                    "plan_id": "test-plan-1",
                    "start_date": "2025-02-01"
                }
            )
            assert response.status_code == 425
            data = response.json()
            assert "status" in data
            assert "not loaded" in data["status"].lower()
        finally:
            globals_.locker = original_locker


class TestFreeAudByCorpus:
    """Тесты для GET /api/free-aud/by-corpus - поиск свободных аудиторий по корпусу"""

    def test_200_free_aud_by_corpus_success(self):
        """Успешный поиск свободных аудиторий по корпусу"""
        response = client.get(
            "/api/free-aud/by-corpus",
            params={
                "corpus_id": "av-test",
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_200_free_aud_by_corpus_with_filters(self):
        """Поиск свободных аудиторий по корпусу с фильтрами"""
        response = client.get(
            "/api/free-aud/by-corpus",
            params={
                "corpus_id": "av-test",
                "start_date": "2025-02-01",
                "end_date": "2025-06-30",
                "day": "thursday"
            }
        )
        assert response.status_code == 200

    def test_422_free_aud_by_corpus_missing_corpus_id(self):
        """Ошибка валидации при отсутствии corpus_id"""
        response = client.get(
            "/api/free-aud/by-corpus",
            params={
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 422

    def test_422_free_aud_by_corpus_missing_start_date(self):
        """Ошибка валидации при отсутствии start_date"""
        response = client.get(
            "/api/free-aud/by-corpus",
            params={
                "corpus_id": "av-test"
            }
        )
        assert response.status_code == 422

    def test_425_free_aud_by_corpus_schedule_not_loaded(self):
        """Тест для проверки статуса 425 когда расписание не загружено"""
        original_locker = globals_.locker

        try:
            globals_.locker = True

            response = client.get(
                "/api/free-aud/by-corpus",
                params={
                    "corpus_id": "av-test",
                    "start_date": "2025-02-01"
                }
            )
            assert response.status_code == 425
            data = response.json()
            assert "status" in data
            assert "not loaded" in data["status"].lower()
        finally:
            globals_.locker = original_locker


class TestFreeAudByLocation:
    """Тесты для GET /api/free-aud/by-loc - поиск свободных аудиторий по локации"""

    def test_200_free_aud_by_loc_success(self):
        """Успешный поиск свободных аудиторий по локации"""
        response = client.get(
            "/api/free-aud/by-loc",
            params={
                "loc_id": "AV",
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_200_free_aud_by_loc_with_filters(self):
        """Поиск свободных аудиторий по локации с фильтрами"""
        response = client.get(
            "/api/free-aud/by-loc",
            params={
                "loc_id": "AV",
                "start_date": "2025-02-01",
                "end_date": "2025-06-30",
                "day": "saturday",
                "para": "4"
            }
        )
        assert response.status_code == 200

    def test_422_free_aud_by_loc_missing_loc_id(self):
        """Ошибка валидации при отсутствии loc_id"""
        response = client.get(
            "/api/free-aud/by-loc",
            params={
                "start_date": "2025-02-01"
            }
        )
        assert response.status_code == 422

    def test_422_free_aud_by_loc_missing_start_date(self):
        """Ошибка валидации при отсутствии start_date"""
        response = client.get(
            "/api/free-aud/by-loc",
            params={
                "loc_id": "AV"
            }
        )
        assert response.status_code == 422

    def test_425_free_aud_by_loc_schedule_not_loaded(self):
        """Тест для проверки статуса 425 когда расписание не загружено"""
        original_locker = globals_.locker

        try:
            globals_.locker = True

            response = client.get(
                "/api/free-aud/by-loc",
                params={
                    "loc_id": "AV",
                    "start_date": "2025-02-01"
                }
            )
            assert response.status_code == 425
            data = response.json()
            assert "status" in data
            assert "not loaded" in data["status"].lower()
        finally:
            globals_.locker = original_locker

    def test_200_free_aud_different_days(self):
        """Проверка разных дней недели"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

        for day in days:
            response = client.get(
                "/api/free-aud/by-loc",
                params={
                    "loc_id": "AV",
                    "start_date": "2025-02-01",
                    "day": day
                }
            )
            assert response.status_code == 200
