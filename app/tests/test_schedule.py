"""Тесты для эндпоинта GET /api/get/schedule"""

import pytest
from .base import client
import app.globals as globals_


class TestGetSchedule:
    """Тесты для GET /api/get/schedule - получение расписания"""

    def test_200_get_all_schedule(self):
        """Успешное получение всего расписания"""
        response = client.get("/api/get/schedule")
        assert response.status_code == 200
        data = response.json()

        # Проверяем, что возвращается расписание с нашей тестовой аудиторией
        assert "test-101" in data
        assert data["test-101"]["id"] == "test-101"
        assert "rasp" in data["test-101"]
        assert "monday" in data["test-101"]["rasp"]

    def test_200_get_schedule_for_auditory(self):
        """Успешное получение расписания для конкретной аудитории"""
        response = client.get("/api/get/schedule?auditory=test-101")
        assert response.status_code == 200
        data = response.json()

        # Проверяем структуру ответа для конкретной аудитории
        assert data["id"] == "test-101"
        assert "rasp" in data
        assert "monday" in data["rasp"]
        assert "1" in data["rasp"]["monday"]
        assert len(data["rasp"]["monday"]["1"]) > 0

        # Проверяем структуру занятия
        lesson = data["rasp"]["monday"]["1"][0]
        assert "groupNames" in lesson
        assert "discipline" in lesson
        assert "teachers" in lesson
        assert lesson["discipline"] == "Математический анализ"

    def test_200_check_schedule_structure(self):
        """Проверка корректности структуры расписания"""
        response = client.get("/api/get/schedule?auditory=test-101")
        assert response.status_code == 200
        data = response.json()

        # Проверяем дни недели
        rasp = data["rasp"]
        expected_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        for day in expected_days:
            assert day in rasp

        # Проверяем структуру занятий в понедельник
        monday_lessons = rasp["monday"]
        assert "1" in monday_lessons  # Первая пара
        assert "2" in monday_lessons  # Вторая пара

        # Проверяем структуру одного занятия
        first_lesson = monday_lessons["1"][0]
        assert isinstance(first_lesson["groupNames"], list)
        assert isinstance(first_lesson["teachers"], list)
        assert "221-011" in first_lesson["groupNames"]
        assert "Иванов И.И." in first_lesson["teachers"]

    def test_425_schedule_not_loaded(self):
        """Тест для проверки статуса 425 когда расписание не загружено (global_rasp=None)"""
        # Сохраняем текущее состояние
        original_rasp = globals_.global_rasp

        try:
            # Устанавливаем global_rasp=None для имитации отсутствия расписания
            globals_.global_rasp = None

            response = client.get("/api/get/schedule")
            assert response.status_code == 425
            data = response.json()
            assert "status" in data
            assert "not loaded" in data["status"].lower()
        finally:
            # Восстанавливаем состояние
            globals_.global_rasp = original_rasp

    def test_200_schedule_with_multiple_lessons(self):
        """Проверка расписания с несколькими занятиями в разные дни"""
        response = client.get("/api/get/schedule?auditory=test-101")
        assert response.status_code == 200
        data = response.json()

        # Проверяем понедельник - должно быть 2 занятия
        monday = data["rasp"]["monday"]
        assert "1" in monday  # Первая пара
        assert "2" in monday  # Вторая пара

        # Проверяем вторник - должно быть 1 занятие
        tuesday = data["rasp"]["tuesday"]
        assert "1" in tuesday
        assert len(tuesday["1"]) == 1
        assert tuesday["1"][0]["discipline"] == "Физика"

        # Проверяем среду - должно быть пусто
        wednesday = data["rasp"]["wednesday"]
        assert len(wednesday) == 0
