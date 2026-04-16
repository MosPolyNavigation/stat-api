"""Тесты валидации JSON-массивов в GraphQL-мутациях для locations, campus, plan."""

from app.tests.base import client

ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str, variables: dict = None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    return client.post("/api/graphql", json=body, headers=ADMIN_HEADERS)


def has_error_with_code(data: dict, code: str) -> bool:
    """Проверяет, что в ответе есть GraphQL-ошибка с нужным кодом."""
    errors = data.get("errors", [])
    for err in errors:
        extensions = err.get("extensions") or {}
        if extensions.get("code") == code:
            return True
    return False


# ---------------------------------------------------------------------------
# NAV LOCATION — поле crossings
# ---------------------------------------------------------------------------

class TestNavLocationCrossingsValidation:

    def test_create_location_with_valid_crossings(self):
        """Создание локации с валидным JSON-массивом crossings."""
        mutation = """
        mutation {
            createNavLocation(data: {
                idSys: "V1"
                name: "Validation Test 1"
                short: "V1"
                ready: false
                address: "Test address 1"
                metro: "Test metro"
                crossings: "[{\\"id\\": 1}]"
            }) {
                id
                crossings
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createNavLocation"]["crossings"] == '[{"id": 1}]'

    def test_create_location_default_crossings_when_null(self):
        """При создании без crossings поле устанавливается в '[]'."""
        mutation = """
        mutation {
            createNavLocation(data: {
                idSys: "V2"
                name: "Validation Test 2"
                short: "V2"
                ready: false
                address: "Test address 2"
                metro: "Test metro"
            }) {
                id
                crossings
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createNavLocation"]["crossings"] == "[]"

    def test_create_location_invalid_crossings_string(self):
        """Невалидный JSON в crossings при создании → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavLocation(data: {
                idSys: "V3"
                name: "Validation Test 3"
                short: "V3"
                ready: false
                address: "Test address 3"
                metro: "Test metro"
                crossings: "not-valid-json"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_create_location_crossings_is_object_not_array(self):
        """JSON-объект вместо массива в crossings → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavLocation(data: {
                idSys: "V4"
                name: "Validation Test 4"
                short: "V4"
                ready: false
                address: "Test address 4"
                metro: "Test metro"
                crossings: "{\\"key\\": \\"value\\"}"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_create_location_crossings_is_number(self):
        """Число вместо массива в crossings → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavLocation(data: {
                idSys: "V5"
                name: "Validation Test 5"
                short: "V5"
                ready: false
                address: "Test address 5"
                metro: "Test metro"
                crossings: "42"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_update_location_valid_crossings(self):
        """Обновление crossings валидным массивом — успешно."""
        mutation = """
        mutation {
            updateNavLocation(id: 1, data: {
                crossings: "[]"
            }) {
                id
                crossings
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["updateNavLocation"]["crossings"] == "[]"

    def test_update_location_invalid_crossings(self):
        """Обновление crossings невалидным JSON → BAD_USER_INPUT."""
        mutation = """
        mutation {
            updateNavLocation(id: 1, data: {
                crossings: "{broken"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")


# ---------------------------------------------------------------------------
# NAV CAMPUS — поле stair_groups
# ---------------------------------------------------------------------------

class TestNavCampusStairGroupsValidation:

    def test_create_campus_with_valid_stair_groups(self):
        """Создание campus с валидным JSON-массивом stair_groups."""
        mutation = """
        mutation {
            createNavCampus(data: {
                idSys: "vt-campus-1"
                locId: 1
                name: "VT Campus 1"
                ready: false
                stairGroups: "[1, 2, 3]"
            }) {
                id
                stairGroups
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createNavCampus"]["stairGroups"] == "[1, 2, 3]"

    def test_create_campus_default_stair_groups_when_null(self):
        """При создании без stair_groups поле устанавливается в '[]'."""
        mutation = """
        mutation {
            createNavCampus(data: {
                idSys: "vt-campus-2"
                locId: 1
                name: "VT Campus 2"
                ready: false
            }) {
                id
                stairGroups
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["createNavCampus"]["stairGroups"] == "[]"

    def test_create_campus_invalid_stair_groups(self):
        """Невалидный JSON в stair_groups → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavCampus(data: {
                idSys: "vt-campus-3"
                locId: 1
                name: "VT Campus 3"
                ready: false
                stairGroups: "not-json"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_create_campus_stair_groups_is_object(self):
        """JSON-объект вместо массива в stair_groups → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavCampus(data: {
                idSys: "vt-campus-4"
                locId: 1
                name: "VT Campus 4"
                ready: false
                stairGroups: "{\\"group\\": 1}"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_update_campus_valid_stair_groups(self):
        """Обновление stair_groups валидным массивом — успешно."""
        mutation = """
        mutation {
            updateNavCampus(id: 1, data: {
                stairGroups: "[]"
            }) {
                id
                stairGroups
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert data["data"]["updateNavCampus"]["stairGroups"] == "[]"

    def test_update_campus_invalid_stair_groups(self):
        """Обновление stair_groups невалидным JSON → BAD_USER_INPUT."""
        mutation = """
        mutation {
            updateNavCampus(id: 1, data: {
                stairGroups: "invalid"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")


# ---------------------------------------------------------------------------
# NAV PLAN — поля entrances и graph
# ---------------------------------------------------------------------------

class TestNavPlanJsonValidation:

    def test_create_plan_with_valid_entrances_and_graph(self):
        """Создание плана с валидными JSON-массивами entrances и graph."""
        mutation = """
        mutation {
            createNavPlan(data: {
                idSys: "vt-plan-1"
                corId: 1
                floorId: 1
                ready: false
                entrances: "[{\\"id\\": \\"e1\\"}]"
                graph: "[{\\"from\\": \\"e1\\", \\"to\\": \\"e2\\"}]"
            }) {
                id
                entrances
                graph
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        result = data["data"]["createNavPlan"]
        assert result["entrances"] == '[{"id": "e1"}]'
        assert result["graph"] == '[{"from": "e1", "to": "e2"}]'

    def test_create_plan_default_when_fields_omitted(self):
        """При создании без entrances/graph оба поля устанавливаются в '[]'."""
        mutation = """
        mutation {
            createNavPlan(data: {
                idSys: "vt-plan-2"
                corId: 1
                floorId: 1
                ready: false
            }) {
                id
                entrances
                graph
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        result = data["data"]["createNavPlan"]
        assert result["entrances"] == "[]"
        assert result["graph"] == "[]"

    def test_create_plan_invalid_entrances(self):
        """Невалидный JSON в entrances → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavPlan(data: {
                idSys: "vt-plan-3"
                corId: 1
                floorId: 1
                ready: false
                entrances: "{not: json}"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_create_plan_invalid_graph(self):
        """Невалидный JSON в graph → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavPlan(data: {
                idSys: "vt-plan-4"
                corId: 1
                floorId: 1
                ready: false
                graph: "not-an-array"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_create_plan_entrances_is_object(self):
        """JSON-объект вместо массива в entrances → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavPlan(data: {
                idSys: "vt-plan-5"
                corId: 1
                floorId: 1
                ready: false
                entrances: "{\\"key\\": \\"val\\"}"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_create_plan_graph_is_object(self):
        """JSON-объект вместо массива в graph → BAD_USER_INPUT."""
        mutation = """
        mutation {
            createNavPlan(data: {
                idSys: "vt-plan-6"
                corId: 1
                floorId: 1
                ready: false
                graph: "{\\"nodes\\": []}"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_update_plan_valid_entrances_and_graph(self):
        """Обновление entrances и graph валидными массивами — успешно."""
        mutation = """
        mutation {
            updateNavPlan(id: 1, data: {
                entrances: "[]"
                graph: "[]"
            }) {
                id
                entrances
                graph
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        result = data["data"]["updateNavPlan"]
        assert result["entrances"] == "[]"
        assert result["graph"] == "[]"

    def test_update_plan_invalid_entrances(self):
        """Обновление entrances невалидным JSON → BAD_USER_INPUT."""
        mutation = """
        mutation {
            updateNavPlan(id: 1, data: {
                entrances: "broken"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")

    def test_update_plan_invalid_graph(self):
        """Обновление graph невалидным JSON → BAD_USER_INPUT."""
        mutation = """
        mutation {
            updateNavPlan(id: 1, data: {
                graph: "{\\"broken\\": true}"
            }) {
                id
            }
        }
        """
        response = graphql_query(mutation)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert has_error_with_code(data, "BAD_USER_INPUT")
