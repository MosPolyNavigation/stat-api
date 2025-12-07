"""Тесты для эндпоинтов отзывов /api/review"""

import pytest
from .base import client

# Токен администратора из base.py (пользователь с полными правами)
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


class TestGetReviewStatuses:
    """Тесты для GET /api/review/statuses - получение списка статусов отзывов"""

    def test_200_get_review_statuses_success(self):
        """Успешное получение списка всех статусов отзывов"""
        response = client.get("/api/review/statuses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Должен быть хотя бы один статус

        # Проверяем структуру каждого статуса
        for status in data:
            assert "id" in status
            assert "name" in status
            assert isinstance(status["id"], int)
            assert isinstance(status["name"], str)
            assert len(status["name"]) > 0

    def test_200_get_review_statuses_contains_expected_statuses(self):
        """Проверка наличия ожидаемых статусов в списке"""
        response = client.get("/api/review/statuses")
        assert response.status_code == 200
        data = response.json()

        # Из base.py мы знаем, что review_status инициализируется в БД
        status_names = [status["name"] for status in data]
        assert len(status_names) > 0
        # Проверяем что все статусы имеют уникальные id и имена
        status_ids = [status["id"] for status in data]
        assert len(status_ids) == len(set(status_ids))  # Все id уникальны
        assert len(status_names) == len(set(status_names))  # Все имена уникальны


class TestSetReviewStatus:
    """Тесты для PATCH /api/review/{review_id}/status - назначение статуса отзыву"""

    def test_200_set_review_status_success(self):
        """Успешное назначение статуса отзыву"""
        # Сначала получим список доступных статусов
        statuses_response = client.get("/api/review/statuses")
        assert statuses_response.status_code == 200
        statuses = statuses_response.json()
        assert len(statuses) > 0
        test_status = statuses[0]

        # Создадим отзыв для теста (используя эндпоинт добавления отзыва)
        # Предполагается что есть эндпоинт POST /api/review
        review_response = client.post(
            "/api/review",
            json={
                "text": "Тестовый отзыв для проверки статусов",
                "rating": 5
            }
        )

        # Если review создается успешно
        if review_response.status_code == 201:
            review_id = review_response.json()["id"]

            # Назначаем статус
            response = client.patch(
                f"/api/review/{review_id}/status",
                data={
                    "status_id": test_status["id"]
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "review_id" in data
            assert "status_id" in data
            assert "status_name" in data
            assert data["review_id"] == review_id
            assert data["status_id"] == test_status["id"]
            assert data["status_name"] == test_status["name"]
            assert "обновлён" in data["message"].lower()

    def test_404_set_review_status_review_not_found(self):
        """Ошибка 404 при попытке назначить статус несуществующему отзыву"""
        # Получаем валидный статус
        statuses_response = client.get("/api/review/statuses")
        statuses = statuses_response.json()
        test_status = statuses[0]

        response = client.patch(
            "/api/review/99999/status",
            data={
                "status_id": test_status["id"]
            }
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "не найден" in data["detail"].lower() or "отзыв" in data["detail"].lower()

    def test_404_set_review_status_status_not_found(self):
        """Ошибка 404 при попытке назначить несуществующий статус"""
        # Создаём отзыв
        review_response = client.post(
            "/api/review",
            json={
                "text": "Отзыв для теста несуществующего статуса",
                "rating": 4
            }
        )

        if review_response.status_code == 201:
            review_id = review_response.json()["id"]

            # Пытаемся назначить несуществующий статус
            response = client.patch(
                f"/api/review/{review_id}/status",
                data={
                    "status_id": 99999
                }
            )
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "статус" in data["detail"].lower() and "не найден" in data["detail"].lower()

    def test_422_set_review_status_missing_status_id(self):
        """Ошибка валидации при отсутствии status_id"""
        response = client.patch(
            "/api/review/1/status",
            data={}
        )
        assert response.status_code == 422

    def test_422_set_review_status_invalid_review_id(self):
        """Ошибка валидации при невалидном ID отзыва"""
        statuses_response = client.get("/api/review/statuses")
        statuses = statuses_response.json()
        test_status = statuses[0]

        response = client.patch(
            "/api/review/invalid/status",
            data={
                "status_id": test_status["id"]
            }
        )
        assert response.status_code == 422

    def test_422_set_review_status_invalid_status_id(self):
        """Ошибка валидации при невалидном status_id"""
        response = client.patch(
            "/api/review/1/status",
            data={
                "status_id": "invalid"
            }
        )
        assert response.status_code == 422
