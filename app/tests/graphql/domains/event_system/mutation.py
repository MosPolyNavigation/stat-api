"""Integration tests for GraphQL Mutation operations in event_system domain."""

import pytest
from app.tests.graphql.base import graphql_query

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def _get_first_node_id(list_field: str) -> int | None:
    """Утилита: получает ID первой записи из списка (простой Int)."""
    resp = graphql_query(
        f"{{ {list_field}(pagination: {{ pageSize: 1 }}) {{ nodes {{ id }} }} }}",
        headers=ADMIN_HEADERS
    )
    if resp["status_code"] == 200 and resp["data"].get("data"):
        nodes = resp["data"]["data"][list_field]["nodes"]
        if nodes:
            return nodes[0]["id"]
    return None


# =============================================================================
# EventType Mutations
# =============================================================================
class TestGraphQLMutationsEventType:
    def test_200_crud_event_type_full_cycle(self):
        # 1. CREATE
        create_query = """
        mutation {
            createEventType(data: {
                codeName: "test_mutation_et"
                description: "Initial description"
            }) {
                id
                codeName
                description
            }
        }
        """
        resp = graphql_query(create_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" not in resp["data"]
        created = resp["data"]["data"]["createEventType"]
        assert created["codeName"] == "test_mutation_et"
        node_id = created["id"]  # Простой Int

        # 2. UPDATE (id: Int!)
        update_query = f"""
        mutation {{
            updateEventType(
                id: {node_id}
                data: {{ description: "Updated description" }}
            ) {{
                id
                description
            }}
        }}
        """
        resp = graphql_query(update_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        updated = resp["data"]["data"]["updateEventType"]
        assert updated["description"] == "Updated description"

        # 3. DELETE (id: Int!)
        delete_query = f"mutation {{ deleteEventType(id: {node_id}) }}"
        resp = graphql_query(delete_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["deleteEventType"] is True

    def test_400_create_duplicate_code_name(self):
        create_query = """
        mutation {
            createEventType(data: { codeName: "site" }) { id }
        }
        """
        resp = graphql_query(create_query, headers=ADMIN_HEADERS)
        if resp["status_code"] == 200:
            assert "errors" in resp["data"]
            assert any("unique" in e["message"].lower() or "duplicate" in e["message"].lower()
                       for e in resp["data"]["errors"])


# =============================================================================
# PayloadType Mutations
# =============================================================================
class TestGraphQLMutationsPayloadType:
    def test_200_crud_payload_type_full_cycle(self):
        # Получаем валидный valueTypeId из сидов (простой Int)
        vt_id_resp = graphql_query("{ valueTypes(pagination: { pageSize: 1 }) { nodes { id } } }", headers=ADMIN_HEADERS)
        vt_raw_id = vt_id_resp["data"]["data"]["valueTypes"]["nodes"][0]["id"]

        # 1. CREATE
        create_query = f"""
        mutation {{
            createPayloadType(data: {{
                codeName: "test_mutation_pt"
                valueTypeId: {vt_raw_id}
                description: "Test payload"
            }}) {{
                id
                codeName
                valueTypeId
            }}
        }}
        """
        resp = graphql_query(create_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" not in resp["data"]
        created = resp["data"]["data"]["createPayloadType"]
        assert created["codeName"] == "test_mutation_pt"
        node_id = created["id"]

        # 2. UPDATE
        update_query = f"""
        mutation {{
            updatePayloadType(
                id: {node_id}
                data: {{ description: "Updated payload type" }}
            ) {{
                description
            }}
        }}
        """
        resp = graphql_query(update_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["updatePayloadType"]["description"] == "Updated payload type"

        # 3. DELETE
        delete_query = f"mutation {{ deletePayloadType(id: {node_id}) }}"
        resp = graphql_query(delete_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["deletePayloadType"] is True


# =============================================================================
# Review Mutations
# =============================================================================
class TestGraphQLMutationsReview:
    def test_200_update_review_partial_fields(self):
        review_id = _get_first_node_id("reviews")
        if not review_id:
            pytest.skip("No reviews in test DB to update")

        update_query = f"""
        mutation {{
            updateReview(
                id: {review_id}
                data: {{ text: "Updated via test mutation", statusId: 3 }}
            ) {{
                id
                text
                status {{ name }}
            }}
        }}
        """
        resp = graphql_query(update_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" not in resp["data"]
        data = resp["data"]["data"]["updateReview"]
        assert data["text"] == "Updated via test mutation"
        assert data["status"]["name"] is not None


# =============================================================================
# AllowedPayloadRule Mutations (составной ключ)
# =============================================================================
class TestGraphQLMutationsAllowedPayloadRule:
    def test_400_create_duplicate_rule(self):
        et_raw = 3
        pt_raw = 1

        create_query = f"""
        mutation {{
            createAllowedPayloadRule(data: {{ eventTypeId: {et_raw}, payloadTypeId: {pt_raw} }}) {{ eventTypeId }}
        }}
        """
        graphql_query(create_query, headers=ADMIN_HEADERS)  # Первый раз — создаём
        resp2 = graphql_query(create_query, headers=ADMIN_HEADERS)  # Второй раз — дубликат
        assert resp2["status_code"] == 200
        assert "errors" in resp2["data"]
        assert any("существует" in e["message"].lower() or "exists" in e["message"].lower()
                   for e in resp2["data"]["errors"])


# =============================================================================
# Права доступа: неавторизованные мутации
# =============================================================================
class TestGraphQLMutationsUnauthorized:
    def test_401_create_without_token(self):
        query = 'mutation { createEventType(data: { codeName: "unauthorized" }) { id } }'
        resp = graphql_query(query)
        assert resp["status_code"] == 401

    def test_401_update_without_token(self):
        query = 'mutation { updateEventType(id: 1, data: { description: "hack" }) { id } }'
        resp = graphql_query(query)
        assert resp["status_code"] == 401

    def test_401_delete_without_token(self):
        query = 'mutation { deleteEventType(id: 1) }'
        resp = graphql_query(query)
        assert resp["status_code"] == 401


# =============================================================================
# Edge-кейсы и обработка ошибок
# =============================================================================
class TestGraphQLMutationsEdgeCases:
    def test_400_update_non_existent_id(self):
        query = 'mutation { updateEventType(id: 999999, data: { description: "ghost" }) { id } }'
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("not found" in e["message"].lower() for e in resp["data"]["errors"])

    def test_400_invalid_id_format(self):
        query = 'mutation { deleteEventType(id: "not-an-int") }'
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]

    def test_400_missing_required_fields_in_create(self):
        query = 'mutation { createEventType(data: { description: "missing codeName" }) { id } }'
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("codeName" in e["message"] or "required" in e["message"].lower()
                   for e in resp["data"]["errors"])


# =============================================================================
# Dashboard Mutation Tests
# =============================================================================
class TestGraphQLDashboardMutation:
    """Тесты для мутаций Dashboard."""

    def test_200_crud_dashboard_full_cycle(self):
        # 1. CREATE
        create_query = """
        mutation {
            createDashboard(data: {
                displayOrder: 100, eventTypeId: 1, dashboardTypeId: 1,
                titleText: "test-mutation-dashboard"
            }) { id displayOrder titleText }
        }
        """
        resp = graphql_query(create_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" not in resp["data"]
        created = resp["data"]["data"]["createDashboard"]
        assert created["titleText"] == "test-mutation-dashboard"
        dashboard_id = created["id"]  # Простой Int

        # 2. UPDATE (id: Int!)
        update_query = f"""
        mutation {{
            updateDashboard(
                id: {dashboard_id}
                data: {{
                    displayOrder: 200, eventTypeId: 1, dashboardTypeId: 1,
                    titleText: "updated-test-dashboard"
                }}
            ) {{ id displayOrder titleText }}
        }}
        """
        resp = graphql_query(update_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        updated = resp["data"]["data"]["updateDashboard"]
        assert updated["displayOrder"] == 200
        assert updated["titleText"] == "updated-test-dashboard"

        # 3. DELETE (id: Int!)
        delete_query = f"mutation {{ deleteDashboard(id: {dashboard_id}) }}"
        resp = graphql_query(delete_query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["deleteDashboard"] is True

        # Verify deletion
        verify_query = f'{{ dashboard(id: {dashboard_id}) {{ id }} }}'
        resp = graphql_query(verify_query, headers=ADMIN_HEADERS)
        assert resp["data"]["data"]["dashboard"] is None

    def test_200_create_dashboards_bulk(self):
        query = """
        mutation {
            createDashboards(inputs: [
                { displayOrder: 301, eventTypeId: 1, dashboardTypeId: 1, titleText: "bulk-1" },
                { displayOrder: 302, eventTypeId: 1, dashboardTypeId: 1, titleText: "bulk-2" }
            ]) { id titleText displayOrder }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" not in resp["data"]
        created = resp["data"]["data"]["createDashboards"]
        assert len(created) == 2
        assert created[0]["titleText"] == "bulk-1"
        assert created[1]["displayOrder"] == 302
        # Cleanup
        for item in created:
            graphql_query(f"mutation {{ deleteDashboard(id: {item['id']}) }}", headers=ADMIN_HEADERS)

    def test_400_create_dashboard_validation_errors(self):
        query = """
        mutation {
            createDashboard(data: {
                displayOrder: 1, eventTypeId: 1, dashboardTypeId: 1, titleText: ""
            }) { id }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("title_text" in e["message"].lower() for e in resp["data"]["errors"])

        query = """
        mutation {
            createDashboard(data: {
                displayOrder: -1, eventTypeId: 1, dashboardTypeId: 1, titleText: "test"
            }) { id }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert "errors" in resp["data"]
        assert any("display_order" in e["message"].lower() for e in resp["data"]["errors"])

    def test_400_create_dashboard_invalid_fk(self):
        query = """
        mutation {
            createDashboard(data: {
                displayOrder: 1, eventTypeId: 99999, dashboardTypeId: 1, titleText: "test"
            }) { id }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("EventType" in e["message"] and "не найден" in e["message"]
                   for e in resp["data"]["errors"])

    def test_404_update_non_existent_dashboard(self):
        query = """
        mutation {
            updateDashboard(
                id: 99999,
                data: { displayOrder: 1, eventTypeId: 1, dashboardTypeId: 1, titleText: "test" }
            ) { id }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("not found" in e["message"].lower() or "не найден" in e["message"]
                   for e in resp["data"]["errors"])

    def test_401_dashboard_mutations_without_token(self):
        mutations = [
            'mutation { createDashboard(data: { displayOrder: 1, eventTypeId: 1, dashboardTypeId: 1, titleText: "test" }) { id } }',  # noqa
            'mutation { updateDashboard(id: 1, data: { displayOrder: 1, eventTypeId: 1, dashboardTypeId: 1, titleText: "test" }) { id } }',  # noqa
            'mutation { deleteDashboard(id: 1) }',
        ]
        for mutation in mutations:
            resp = graphql_query(mutation)
            assert resp["status_code"] == 401
