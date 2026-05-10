"""Integration tests for GraphQL Mutation operations in navigation domain."""
import pytest  # noqa
from app.tests.base import client

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str, headers: dict = None, variables: dict = None):
    return client.post(
        "/api/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers or {},
    )


# =============================================================================
# NavLocation Mutations
# =============================================================================
class TestGraphQLMutationsNavLocation:
    def test_200_crud_nav_location_full_cycle(self):
        create_q = """
        mutation {
            createNavLocation(data: {
                idSys: "test-loc", name: "Test Location", short: "TL",
                ready: true, address: "Test St", metro: "Test Metro"
            }) { id idSys name }
        }
        """
        r = graphql_query(create_q, ADMIN_HEADERS)
        assert r.status_code == 200
        assert "errors" not in r.json()
        loc = r.json()["data"]["createNavLocation"]
        assert loc["idSys"] == "test-loc"
        loc_id = loc["id"]

        update_q = f"""
        mutation {{
            updateNavLocation(id: {loc_id}, data: {{ name: "Updated Location" }})
            {{ id name }}
        }}
        """
        r = graphql_query(update_q, ADMIN_HEADERS)
        assert r.json()["data"]["updateNavLocation"]["name"] == "Updated Location"

        delete_q = f"mutation {{ deleteNavLocation(id: {loc_id}) }}"
        r = graphql_query(delete_q, ADMIN_HEADERS)
        assert r.json()["data"]["deleteNavLocation"] is True

        verify_q = f"{{ navLocation(id: {loc_id}) {{ id }} }}"
        r = graphql_query(verify_q, ADMIN_HEADERS)
        assert r.json()["data"]["navLocation"] is None

    def test_400_create_nav_location_validation(self):
        q = """
        mutation {
            createNavLocation(data: { name: "No idSys" }) { id }
        }
        """
        r = graphql_query(q, ADMIN_HEADERS)
        assert "errors" in r.json()


# =============================================================================
# NavCampus Mutations
# =============================================================================
class TestGraphQLMutationsNavCampus:
    def test_200_crud_nav_campus_full_cycle(self):
        create_q = """
        mutation {
            createNavCampus(data: {
                idSys: "test-campus", locId: 1, name: "Test Campus",
                ready: true
            }) { id idSys name }
        }
        """
        r = graphql_query(create_q, ADMIN_HEADERS)
        assert "errors" not in r.json()
        campus = r.json()["data"]["createNavCampus"]
        campus_id = campus["id"]

        update_q = f"""
        mutation {{
            updateNavCampus(id: {campus_id}, data: {{ name: "Updated Campus" }})
            {{ name }}
        }}
        """
        r = graphql_query(update_q, ADMIN_HEADERS)
        assert r.json()["data"]["updateNavCampus"]["name"] == "Updated Campus"

        delete_q = f"mutation {{ deleteNavCampus(id: {campus_id}) }}"
        r = graphql_query(delete_q, ADMIN_HEADERS)
        assert r.json()["data"]["deleteNavCampus"] is True


# =============================================================================
# NavPlan Mutations (с валидацией JSON-полей)
# =============================================================================
class TestGraphQLMutationsNavPlan:
    def test_200_create_nav_plan_with_json_fields(self):
        # Упрощённый JSON для избежания конфликтов с GraphQL-парсером
        create_q = """
        mutation {
            createNavPlan(data: {
                idSys: "test-plan", corId: 1, floorId: 1, ready: true,
                entrances: "[1, 2]",
                graph: "[{}]"
            }) { id idSys entrances graph }
        }
        """
        r = graphql_query(create_q, ADMIN_HEADERS)
        assert "errors" not in r.json()
        plan = r.json()["data"]["createNavPlan"]
        assert plan["entrances"] == "[1, 2]"

    def test_400_create_nav_plan_invalid_json(self):
        create_q = """
        mutation {
            createNavPlan(data: {
                idSys: "bad-plan", corId: 1, floorId: 1, ready: true,
                entrances: "not-json"
            }) { id }
        }
        """
        r = graphql_query(create_q, ADMIN_HEADERS)
        assert "errors" in r.json()
        assert any("entrances" in e["message"].lower() and "json" in e["message"].lower()
                   for e in r.json()["errors"])


# =============================================================================
# NavAuditory Mutations
# =============================================================================
class TestGraphQLMutationsNavAuditory:
    def test_200_crud_nav_auditory_full_cycle(self):
        create_q = """
        mutation {
            createNavAuditory(data: {
                idSys: "test-aud", typeId: 1, planId: 1, ready: true,
                name: "Test Aud 101"
            }) { id idSys name }
        }
        """
        r = graphql_query(create_q, ADMIN_HEADERS)
        assert "errors" not in r.json()
        aud = r.json()["data"]["createNavAuditory"]
        aud_id = aud["id"]

        update_q = f"""
        mutation {{
            updateNavAuditory(id: {aud_id}, data: {{ name: "Updated Aud" }})
            {{ name }}
        }}
        """
        r = graphql_query(update_q, ADMIN_HEADERS)
        assert r.json()["data"]["updateNavAuditory"]["name"] == "Updated Aud"

        delete_q = f"mutation {{ deleteNavAuditory(id: {aud_id}) }}"
        r = graphql_query(delete_q, ADMIN_HEADERS)
        assert r.json()["data"]["deleteNavAuditory"] is True


# =============================================================================
# NavStatic Mutations
# =============================================================================
class TestGraphQLMutationsNavStatic:
    def test_200_crud_nav_static_full_cycle(self):
        create_q = """
        mutation {
            createNavStatic(data: {
                ext: "png", path: "/files/test.png",
                name: "test.png", link: "/api/static/test.png"
            }) { id name path }
        }
        """
        r = graphql_query(create_q, ADMIN_HEADERS)
        assert "errors" not in r.json()
        static = r.json()["data"]["createNavStatic"]
        static_id = static["id"]

        update_q = f"""
        mutation {{
            updateNavStatic(id: {static_id}, data: {{ name: "updated.png" }})
            {{ name }}
        }}
        """
        r = graphql_query(update_q, ADMIN_HEADERS)
        assert r.json()["data"]["updateNavStatic"]["name"] == "updated.png"

        delete_q = f"mutation {{ deleteNavStatic(id: {static_id}) }}"
        r = graphql_query(delete_q, ADMIN_HEADERS)
        assert r.json()["data"]["deleteNavStatic"] is True


# =============================================================================
# Права доступа для мутаций
# =============================================================================
class TestGraphQLMutationsNavUnauthorized:
    def test_401_create_without_token(self):
        q = 'mutation { createNavLocation(data: { idSys: "x", name: "x", short: "x", ready: true, address: "x", metro: "x" }) { id } }'  # noqa
        r = graphql_query(q)
        assert r.status_code == 401

    def test_401_update_without_token(self):
        q = 'mutation { updateNavLocation(id: 1, data: { name: "hack" }) { id } }'
        r = graphql_query(q)
        assert r.status_code == 401

    def test_401_delete_without_token(self):
        q = 'mutation { deleteNavLocation(id: 1) }'
        r = graphql_query(q)
        assert r.status_code == 401


# =============================================================================
# Edge-кейсы мутаций
# =============================================================================
class TestGraphQLMutationsNavEdgeCases:
    def test_404_update_non_existent_id(self):
        q = f"""
        mutation {{
            updateNavLocation(id: 999999, data: {{ name: "ghost" }}) {{ id }}
        }}
        """
        r = graphql_query(q, ADMIN_HEADERS)
        assert "errors" in r.json()
        assert any("not found" in e["message"].lower() for e in r.json()["errors"])

    def test_200_create_without_fk_validation(self):
        """
        Примечание: Фабрика мутаций не валидирует FK автоматически.
        Мутация успешно создаёт запись, т.к. в CampusResource нет валидатора loc_id.
        """
        q = """
        mutation {
            createNavCampus(data: {
                idSys: "no-fk-check", locId: 999999, name: "Bad", ready: true
            }) { id }
        }
        """
        r = graphql_query(q, ADMIN_HEADERS)
        assert "errors" not in r.json()
        assert r.json()["data"]["createNavCampus"]["id"] is not None
