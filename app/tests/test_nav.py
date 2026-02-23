"""
Тесты для навигационных эндпоинтов /api/nav/*
"""
from app.tests.base import client


class TestNavCampus:
    """Тесты для эндпоинта GET /api/nav/campus"""

    def test_get_campus_success(self):
        """Тест успешного получения информации о кампусе"""
        response = client.get("/api/nav/campus?loc=AV")
        assert response.status_code == 200
        data = response.json()

        # Проверяем структуру ответа
        assert "id" in data
        assert "rusName" in data
        assert "corpuses" in data
        assert "crossings" in data

        # Проверяем данные
        assert data["id"] == "AV"
        assert data["rusName"] == "АВ"
        assert isinstance(data["corpuses"], dict)
        assert isinstance(data["crossings"], list)

    def test_get_campus_with_corpus(self):
        """Тест получения кампуса с корпусами"""
        response = client.get("/api/nav/campus?loc=AV")
        assert response.status_code == 200
        data = response.json()

        # Проверяем, что есть корпус
        assert "av-test" in data["corpuses"]
        corpus = data["corpuses"]["av-test"]

        # Проверяем структуру корпуса
        assert "rusName" in corpus
        assert "planLinks" in corpus
        assert "stairsGroups" in corpus

        # Проверяем данные корпуса
        assert isinstance(corpus["planLinks"], list)
        assert isinstance(corpus["stairsGroups"], list)

    def test_get_campus_plan_links(self):
        """Тест наличия ссылок на планы в корпусе"""
        response = client.get("/api/nav/campus?loc=AV")
        assert response.status_code == 200
        data = response.json()

        corpus = data["corpuses"]["av-test"]
        plan_links = corpus["planLinks"]

        # Должна быть хотя бы одна ссылка на план
        assert len(plan_links) > 0
        assert all(link.startswith("/api/nav/plan?plan=") for link in plan_links)

    def test_get_campus_not_found(self):
        """Тест получения несуществующего кампуса"""
        response = client.get("/api/nav/campus?loc=NONEXISTENT")
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"].lower()

    def test_get_campus_missing_parameter(self):
        """Тест запроса без обязательного параметра loc"""
        response = client.get("/api/nav/campus")
        assert response.status_code == 422


class TestNavPlan:
    """Тесты для эндпоинта GET /api/nav/plan"""

    def test_get_plan_success(self):
        """Тест успешного получения плана"""
        response = client.get("/api/nav/plan?plan=test-plan-1")
        assert response.status_code == 200
        data = response.json()

        # Проверяем структуру ответа
        assert "planName" in data
        assert "svgLink" in data
        assert "campus" in data
        assert "corpus" in data
        assert "floor" in data
        assert "entrances" in data
        assert "graph" in data
        assert "spaces" in data

    def test_get_plan_data_validation(self):
        """Тест валидации данных плана"""
        response = client.get("/api/nav/plan?plan=test-plan-1")
        assert response.status_code == 200
        data = response.json()

        # Проверяем данные
        assert data["planName"] == "test-plan-1"
        assert data["campus"] == "AV"
        assert data["corpus"] == "av-test"
        assert data["floor"] == 1

        # Проверяем типы
        assert isinstance(data["entrances"], list)
        assert isinstance(data["graph"], list)
        assert isinstance(data["spaces"], list)

    def test_get_plan_svg_link(self):
        """Тест наличия/отсутствия SVG ссылки"""
        response = client.get("/api/nav/plan?plan=test-plan-1")
        assert response.status_code == 200
        data = response.json()

        # SVG может быть None (в тестовых данных нет SVG)
        assert "svgLink" in data
        # Если svgLink не None, должна быть строкой
        if data["svgLink"] is not None:
            assert isinstance(data["svgLink"], str)

    def test_get_plan_entrances_and_graph(self):
        """Тест корректности JSON полей entrances и graph"""
        response = client.get("/api/nav/plan?plan=test-plan-1")
        assert response.status_code == 200
        data = response.json()

        # Проверяем, что JSON корректно распарсился
        assert isinstance(data["entrances"], list)
        assert isinstance(data["graph"], list)

    def test_get_plan_not_found(self):
        """Тест получения несуществующего плана"""
        response = client.get("/api/nav/plan?plan=nonexistent-plan")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_plan_missing_parameter(self):
        """Тест запроса без обязательного параметра plan"""
        response = client.get("/api/nav/plan")
        assert response.status_code == 422


class TestNavCampuses:
    """Тесты для эндпоинта GET /api/nav/campuses"""

    def test_get_campuses_success(self):
        """Тест успешного получения списка ссылок на кампусы"""
        response = client.get("/api/nav/campuses")
        assert response.status_code == 200
        data = response.json()

        # Должен вернуться список строк (ссылок)
        assert isinstance(data, list)

    def test_get_campuses_links_format(self):
        """Тест формата ссылок на кампусы"""
        response = client.get("/api/nav/campuses")
        assert response.status_code == 200
        data = response.json()

        # Все элементы должны быть строками
        assert all(isinstance(link, str) for link in data)

        # Все ссылки должны начинаться с /api/nav/campus?loc=
        if len(data) > 0:
            assert all(link.startswith("/api/nav/campus?loc=") for link in data)

    def test_get_campuses_contains_test_location(self):
        """Тест наличия тестовой локации в списке"""
        response = client.get("/api/nav/campuses")
        assert response.status_code == 200
        data = response.json()

        # Ищем ссылку на нашу тестовую локацию AV
        av_link = "/api/nav/campus?loc=AV"
        assert av_link in data
