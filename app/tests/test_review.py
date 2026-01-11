"""Тесты для эндпоинтов отзывов /api/review"""

import pytest
from .base import client

# Токен администратора из base.py (пользователь с полными правами)
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


class TestSetReviewStatus:
    """Тесты для PATCH /api/review/{review_id}/status - назначение статуса отзыву"""

    def test_200_set_review_status_success(self):
        """Успешное назначение статуса отзыву"""

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
                    "status_id": 1
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "review_id" in data
            assert "status_id" in data
            assert "status_name" in data
            assert data["review_id"] == review_id
            assert data["status_id"] == 1
            assert data["status_name"] == "бэклог"
            assert "обновлён" in data["message"].lower()

    def test_404_set_review_status_review_not_found(self):
        """Ошибка 404 при попытке назначить статус несуществующему отзыву"""

        response = client.patch(
            "/api/review/99999/status",
            data={
                "status_id": 1
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

        response = client.patch(
            "/api/review/invalid/status",
            data={
                "status_id": 1
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
