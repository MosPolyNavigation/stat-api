"""
Интеграционные тесты для эндпоинта /api/get/locationData
"""
from app.tests.base import client


class TestLocationData:
    """Тесты для эндпоинта GET /api/get/locationData"""

    def test_get_location_data_success(self):
        """Тест успешного получения данных навигации"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Проверяем наличие всех обязательных ключей
        assert "locations" in data
        assert "corpuses" in data
        assert "plans" in data
        assert "rooms" in data

        # Проверяем что все поля являются списками
        assert isinstance(data["locations"], list)
        assert isinstance(data["corpuses"], list)
        assert isinstance(data["plans"], list)
        assert isinstance(data["rooms"], list)

    def test_location_data_structure(self):
        """Тест структуры данных locations"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Должна быть хотя бы одна локация (из тестовых данных)
        assert len(data["locations"]) > 0

        # Проверяем структуру первой локации
        location = data["locations"][0]
        assert "id" in location
        assert "title" in location
        assert "short" in location
        assert "available" in location
        assert "address" in location
        assert "crossings" in location

        # Проверяем типы данных
        assert isinstance(location["id"], str)
        assert isinstance(location["title"], str)
        assert isinstance(location["short"], str)
        assert isinstance(location["available"], bool)
        assert isinstance(location["address"], str)
        # crossings может быть None или списком кортежей
        assert location["crossings"] is None or isinstance(location["crossings"], list)

    def test_location_data_test_values(self):
        """Тест соответствия данных тестовым значениям из base.py"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Проверяем что тестовая локация "AV" присутствует
        locations = data["locations"]
        av_location = next((loc for loc in locations if loc["id"] == "AV"), None)
        assert av_location is not None

        # Проверяем данные тестовой локации
        assert av_location["title"] == "Автозаводская"
        assert av_location["short"] == "АВ"
        assert av_location["available"] is True
        assert av_location["address"] == "ул. Автозаводская, д. 16"
        # В тестовых данных crossings=None
        assert av_location["crossings"] is None

    def test_corpus_data_structure(self):
        """Тест структуры данных corpuses"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Должен быть хотя бы один корпус
        assert len(data["corpuses"]) > 0

        # Проверяем структуру первого корпуса
        corpus = data["corpuses"][0]
        assert "id" in corpus
        assert "locationId" in corpus
        assert "title" in corpus
        assert "available" in corpus
        assert "stairs" in corpus

        # Проверяем типы данных
        assert isinstance(corpus["id"], str)
        assert isinstance(corpus["locationId"], str)
        assert isinstance(corpus["title"], str)
        assert isinstance(corpus["available"], bool)
        # stairs может быть None или списком
        assert corpus["stairs"] is None or isinstance(corpus["stairs"], list)

    def test_corpus_data_test_values(self):
        """Тест соответствия данных корпуса тестовым значениям"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Проверяем тестовый корпус "av-test"
        corpuses = data["corpuses"]
        test_corpus = next((corp for corp in corpuses if corp["id"] == "av-test"), None)
        assert test_corpus is not None

        # Проверяем данные
        assert test_corpus["locationId"] == "AV"
        assert test_corpus["title"] == "Тестовый корпус"
        assert test_corpus["available"] is True
        # В тестовых данных stair_groups=None
        assert test_corpus["stairs"] is None

    def test_plan_data_structure(self):
        """Тест структуры данных plans"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Должен быть хотя бы один план
        assert len(data["plans"]) > 0

        # Проверяем структуру первого плана
        plan = data["plans"][0]
        assert "id" in plan
        assert "corpusId" in plan
        assert "floor" in plan
        assert "available" in plan
        assert "wayToSvg" in plan
        assert "graph" in plan
        assert "entrances" in plan
        assert "nearest" in plan

        # Проверяем типы данных
        assert isinstance(plan["id"], str)
        assert isinstance(plan["corpusId"], str)
        assert isinstance(plan["floor"], str)
        assert isinstance(plan["available"], bool)
        assert isinstance(plan["wayToSvg"], str)
        assert isinstance(plan["graph"], list)
        assert isinstance(plan["entrances"], list)
        assert isinstance(plan["nearest"], dict)

    def test_plan_nearest_structure(self):
        """Тест структуры nearest в плане"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        plan = data["plans"][0]
        nearest = plan["nearest"]

        # Проверяем наличие всех полей в nearest
        assert "enter" in nearest
        assert "wm" in nearest
        assert "ww" in nearest
        assert "ws" in nearest

        # Проверяем типы: enter должна быть строкой, остальные могут быть None или строкой
        assert isinstance(nearest["enter"], str)
        assert nearest["wm"] is None or isinstance(nearest["wm"], str)
        assert nearest["ww"] is None or isinstance(nearest["ww"], str)
        assert nearest["ws"] is None or isinstance(nearest["ws"], str)

    def test_plan_data_test_values(self):
        """Тест соответствия данных плана тестовым значениям"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Проверяем тестовый план "test-plan-1"
        plans = data["plans"]
        test_plan = next((p for p in plans if p["id"] == "test-plan-1"), None)
        assert test_plan is not None

        # Проверяем данные
        assert test_plan["corpusId"] == "av-test"
        assert test_plan["floor"] == "1"
        assert test_plan["available"] is True
        assert test_plan["wayToSvg"] == ""  # SVG не указан в тестовых данных
        assert test_plan["graph"] == []  # Пустой граф в тестовых данных
        assert test_plan["entrances"] == []  # Пустой список входов

        # Проверяем nearest
        assert test_plan["nearest"]["enter"] == ""
        assert test_plan["nearest"]["wm"] is None
        assert test_plan["nearest"]["ww"] is None
        assert test_plan["nearest"]["ws"] is None

    def test_room_data_structure(self):
        """Тест структуры данных rooms"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Должна быть хотя бы одна комната
        assert len(data["rooms"]) > 0

        # Проверяем структуру первой комнаты
        room = data["rooms"][0]
        assert "id" in room
        assert "planId" in room
        assert "type" in room
        assert "available" in room
        assert "numberOrTitle" in room
        assert "tabletText" in room
        assert "addInfo" in room

        # Проверяем типы данных
        assert isinstance(room["id"], str)
        assert isinstance(room["planId"], str)
        assert isinstance(room["type"], str)
        assert isinstance(room["available"], bool)
        assert isinstance(room["numberOrTitle"], str)
        assert isinstance(room["tabletText"], str)
        assert isinstance(room["addInfo"], str)

    def test_room_data_test_values(self):
        """Тест соответствия данных комнаты тестовым значениям"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Проверяем тестовую аудиторию "test-101"
        rooms = data["rooms"]
        test_room = next((r for r in rooms if r["id"] == "test-101"), None)
        assert test_room is not None

        # Проверяем данные
        assert test_room["planId"] == "test-plan-1"
        assert test_room["type"] == "Учебная аудитория"
        assert test_room["available"] is True
        assert test_room["numberOrTitle"] == "101"
        assert test_room["tabletText"] == ""
        assert test_room["addInfo"] == ""

    def test_location_data_relationships(self):
        """Тест связей между сущностями"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Проверяем что корпус ссылается на существующую локацию
        corpus = next((c for c in data["corpuses"] if c["id"] == "av-test"), None)
        assert corpus is not None
        location_ids = [loc["id"] for loc in data["locations"]]
        assert corpus["locationId"] in location_ids

        # Проверяем что план ссылается на существующий корпус
        plan = next((p for p in data["plans"] if p["id"] == "test-plan-1"), None)
        assert plan is not None
        corpus_ids = [corp["id"] for corp in data["corpuses"]]
        assert plan["corpusId"] in corpus_ids

        # Проверяем что комната ссылается на существующий план
        room = next((r for r in data["rooms"] if r["id"] == "test-101"), None)
        assert room is not None
        plan_ids = [p["id"] for p in data["plans"]]
        assert room["planId"] in plan_ids

    def test_location_data_only_ready_items(self):
        """Тест что возвращаются только готовые (ready=True) элементы"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Все локации должны быть доступны (available=True)
        for location in data["locations"]:
            assert location["available"] is True

        # Все корпуса должны быть доступны
        for corpus in data["corpuses"]:
            assert corpus["available"] is True

        # Все планы должны быть доступны
        for plan in data["plans"]:
            assert plan["available"] is True

        # Все комнаты должны быть доступны
        for room in data["rooms"]:
            assert room["available"] is True

    def test_location_crossings_format(self):
        """Тест формата crossings в локациях"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Если у какой-то локации есть crossings, проверяем формат
        for location in data["locations"]:
            if location["crossings"] is not None:
                assert isinstance(location["crossings"], list)
                # Каждый crossing должен быть списком/кортежем из 3 элементов
                for crossing in location["crossings"]:
                    assert isinstance(crossing, (list, tuple))
                    assert len(crossing) == 3
                    # Первые два элемента - строки (id), третий - число (расстояние)
                    assert isinstance(crossing[0], str)
                    assert isinstance(crossing[1], str)
                    assert isinstance(crossing[2], (int, float))

    def test_corpus_stairs_format(self):
        """Тест формата stairs в корпусах"""
        response = client.get("/api/get/locationData")
        assert response.status_code == 200
        data = response.json()

        # Если у какого-то корпуса есть stairs, проверяем формат
        for corpus in data["corpuses"]:
            if corpus["stairs"] is not None:
                assert isinstance(corpus["stairs"], list)
                # stairs - это список групп лестниц
                for stair_group in corpus["stairs"]:
                    assert isinstance(stair_group, list)
                    # Каждая группа - список строк (id лестниц)
                    for stair_id in stair_group:
                        assert isinstance(stair_id, str)
