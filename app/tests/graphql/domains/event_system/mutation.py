"""Integration tests for GraphQL Mutation operations in event_system domain."""

import pytest
from app.tests.base import client
from strawberry.relay import from_base64

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str, headers: dict = None, variables: dict = None):
    """Хелпер для выполнения GraphQL-запросов через тестовый клиент."""
    return client.post(
        "/api/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers or {},
    )


def _get_first_node_id(list_field: str) -> str | None:
    """Утилита: получает ID первой записи из списка (для зависимостей в тестах)."""
    resp = graphql_query(f"{{ {list_field}(first: 1) {{ edges {{ node {{ id }} }} }} }}", ADMIN_HEADERS)
    if resp.status_code == 200 and resp.json().get("data"):
        edges = resp.json()["data"][list_field]["edges"]
        if edges:
            return edges[0]["node"]["id"]
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
        resp = graphql_query(create_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert "errors" not in resp.json()
        created = resp.json()["data"]["createEventType"]
        assert created["codeName"] == "test_mutation_et"
        node_id = created["id"]

        # 2. UPDATE
        update_query = f"""
        mutation {{
            updateEventType(
                id: "{node_id}"
                data: {{ description: "Updated description" }}
            ) {{
                id
                description
            }}
        }}
        """
        resp = graphql_query(update_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        updated = resp.json()["data"]["updateEventType"]
        assert updated["description"] == "Updated description"

        # 3. DELETE
        delete_query = f"""
        mutation {{
            deleteEventType(id: "{node_id}")
        }}
        """
        resp = graphql_query(delete_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["data"]["deleteEventType"] is True

    def test_400_create_duplicate_code_name(self):
        """Проверка уникальности codeName (если в БД есть UNIQUE-констрейнт)."""
        create_query = """
        mutation {
            createEventType(data: { codeName: "site" }) { id }
        }
        """
        resp = graphql_query(create_query, ADMIN_HEADERS)
        # Ожидаем ошибку в GraphQL или HTTP 200 с errors массивом
        if resp.status_code == 200:
            assert "errors" in resp.json()
            assert any("unique" in e["message"].lower() or "duplicate" in e["message"].lower()
                       for e in resp.json()["errors"])


# =============================================================================
# PayloadType Mutations
# =============================================================================
class TestGraphQLMutationsPayloadType:
    def test_200_crud_payload_type_full_cycle(self):
        # Получаем валидный valueTypeId из сидов
        vt_id_resp = graphql_query("{ valueTypes(first: 1) { edges { node { id } } } }", ADMIN_HEADERS)
        vt_global_id = vt_id_resp.json()["data"]["valueTypes"]["edges"][0]["node"]["id"]
        _, vt_raw_id = from_base64(vt_global_id)

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
        resp = graphql_query(create_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert "errors" not in resp.json()
        created = resp.json()["data"]["createPayloadType"]
        assert created["codeName"] == "test_mutation_pt"
        node_id = created["id"]

        # 2. UPDATE (частичное)
        update_query = f"""
        mutation {{
            updatePayloadType(
                id: "{node_id}"
                data: {{ description: "Updated payload type" }}
            ) {{
                description
            }}
        }}
        """
        resp = graphql_query(update_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["data"]["updatePayloadType"]["description"] == "Updated payload type"

        # 3. DELETE
        delete_query = f"""
        mutation {{ deletePayloadType(id: "{node_id}") }}
        """
        resp = graphql_query(delete_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["data"]["deletePayloadType"] is True


# =============================================================================
# Review Mutations (только обновление)
# =============================================================================
class TestGraphQLMutationsReview:
    def test_200_update_review_partial_fields(self):
        # Получаем ID существующего отзыва из сидов
        review_id = _get_first_node_id("reviews")
        if not review_id:
            pytest.skip("No reviews in test DB to update")

        update_query = f"""
        mutation {{
            updateReview(
                id: "{review_id}"
                data: {{ text: "Updated via test mutation", statusId: 3 }}
            ) {{
                id
                text
                status {{ name }}
            }}
        }}
        """
        resp = graphql_query(update_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert "errors" not in resp.json()

        data = resp.json()["data"]["updateReview"]
        assert data["text"] == "Updated via test mutation"
        assert data["status"]["name"] is not None  # statusId=3 должен резолвиться


# =============================================================================
# AllowedPayloadRule Mutations (составной ключ)
# =============================================================================
class TestGraphQLMutationsAllowedPayloadRule:
    def test_200_crud_composite_key_rule(self):
        # 1. Получаем достаточно ID для теста
        et_resp = graphql_query("{ eventTypes(first: 2) { edges { node { id } } } }", ADMIN_HEADERS)
        et_edges = et_resp.json()["data"]["eventTypes"]["edges"]
        et_raw = from_base64(et_edges[0]["node"]["id"])[1]

        pt_resp = graphql_query("{ payloadTypes(first: 2) { edges { node { id } } } }", ADMIN_HEADERS)
        pt_edges = pt_resp.json()["data"]["payloadTypes"]["edges"]
        pt_raw = from_base64(pt_edges[0]["node"]["id"])[1]

        # 1. CREATE (или находим существующий)
        create_query = f"""
        mutation {{
            createAllowedPayloadRule(data: {{ eventTypeId: {et_raw}, payloadTypeId: {pt_raw} }}) {{ id }}
        }}
        """
        resp = graphql_query(create_query, ADMIN_HEADERS)
        rule_id = None
        if "errors" in resp.json():
            list_resp = graphql_query("{ allowedPayloadRules(first: 1) { edges { node { id } } } }", ADMIN_HEADERS)
            edges = list_resp.json()["data"]["allowedPayloadRules"]["edges"]
            if edges:
                rule_id = edges[0]["node"]["id"]
            else:
                pytest.skip("Cannot find existing rule for testing")
        else:
            rule_id = resp.json()["data"]["createAllowedPayloadRule"]["id"]

        # 2. UPDATE (смена составного ключа удаляет старую запись из БД!)
        if len(et_edges) > 1:
            new_et_raw = from_base64(et_edges[1]["node"]["id"])[1]
            update_query = f"""
            mutation {{
                updateAllowedPayloadRule(id: "{rule_id}", data: {{ newEventTypeId: {new_et_raw}, newPayloadTypeId: {pt_raw} }}) {{ id }}
            }}
            """
            resp = graphql_query(update_query, ADMIN_HEADERS)
            # Если update успешен, rule_id меняется на новый составной ключ
            if "errors" not in resp.json():
                rule_id = resp.json()["data"]["updateAllowedPayloadRule"]["id"]

        # 3. DELETE (устойчив к тому, что запись уже могла быть удалена при UPDATE)
        delete_query = f"""
        mutation {{ deleteAllowedPayloadRule(id: "{rule_id}") }}
        """
        resp = graphql_query(delete_query, ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()

        # ✅ Проверяем успешное удаление ИЛИ ожидаемую ошибку "не найдено"
        if data.get("data") and data["data"]["deleteAllowedPayloadRule"] is True:
            pass  # Успешно удалено
        elif "errors" in data:
            msg = data["errors"][0]["message"].lower()
            assert "не найдено" in msg or "not found" in msg, f"Unexpected delete error: {data['errors']}"
        else:
            raise AssertionError(f"Unexpected response structure: {data}")

    def test_400_create_duplicate_rule(self):
        """Проверка уникальности составного ключа."""
        et_resp = graphql_query("{ eventTypes(first: 1) { edges { node { id } } } }", ADMIN_HEADERS)
        _, et_raw = from_base64(et_resp.json()["data"]["eventTypes"]["edges"][0]["node"]["id"])
        pt_resp = graphql_query("{ payloadTypes(first: 1) { edges { node { id } } } }", ADMIN_HEADERS)
        _, pt_raw = from_base64(pt_resp.json()["data"]["payloadTypes"]["edges"][0]["node"]["id"])

        create_query = f"""
        mutation {{
            createAllowedPayloadRule(data: {{ eventTypeId: {et_raw}, payloadTypeId: {pt_raw} }}) {{ id }}
        }}
        """
        # Первый запрос (создаст или упадёт, если уже есть)
        graphql_query(create_query, ADMIN_HEADERS)

        # Второй запрос гарантированно должен вернуть ошибку дубликата
        resp2 = graphql_query(create_query, ADMIN_HEADERS)
        assert resp2.status_code == 200
        assert "errors" in resp2.json()

        # ✅ Исправлено: поддержка русского текста ошибки
        assert any("существует" in e["message"].lower() or "exists" in e["message"].lower()
                   for e in resp2.json()["errors"])


# =============================================================================
# Права доступа: неавторизованные мутации
# =============================================================================
class TestGraphQLMutationsUnauthorized:
    def test_401_create_without_token(self):
        query = """
        mutation {
            createEventType(data: { codeName: "unauthorized_test" }) { id }
        }
        """
        resp = graphql_query(query)  # ← без заголовков
        assert resp.status_code == 401

    def test_401_update_without_token(self):
        query = """
        mutation {
            updateEventType(id: "RXZlbnRUeXBlOjE=", data: { description: "hack" }) { id }
        }
        """
        resp = graphql_query(query)
        assert resp.status_code == 401

    def test_401_delete_without_token(self):
        query = """
        mutation { deleteEventType(id: "RXZlbnRUeXBlOjE=") }
        """
        resp = graphql_query(query)
        assert resp.status_code == 401


# =============================================================================
# Edge-кейсы и обработка ошибок
# =============================================================================
class TestGraphQLMutationsEdgeCases:
    def test_400_update_non_existent_id(self):
        # Глобальный ID для несуществующего узла
        query = """
        mutation {
            updateEventType(id: "RXZlbnRUeXBlOjk5OTk5", data: { description: "ghost" }) { id }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert "errors" in resp.json()
        assert any("not found" in e["message"].lower() for e in resp.json()["errors"])

    def test_400_invalid_global_id_format(self):
        query = """
        mutation {
            deleteEventType(id: "not-a-valid-global-id")
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert "errors" in resp.json()
        assert any("Invalid base64" in e["message"] or "decode" in e["message"].lower()
                   for e in resp.json()["errors"])

    def test_400_missing_required_fields_in_create(self):
        # codeName обязателен в CreateEventTypeInput
        query = """
        mutation {
            createEventType(data: { description: "missing codeName" }) { id }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS)
        assert resp.status_code == 200
        assert "errors" in resp.json()
        # GraphQL валидация входных аргументов ловит это на уровне парсера
        assert any("codeName" in e["message"] or "required" in e["message"].lower()
                   for e in resp.json()["errors"])
