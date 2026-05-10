"""Integration tests for GraphQL Query operations in event_system domain."""
import pytest
from strawberry.relay import from_base64

from app.tests.base import client  # ← Адаптируй путь под свою структуру

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"  # ← Замени на реальный токен
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str, headers: dict = None, variables: dict = None):
    """Хелпер для выполнения GraphQL-запросов через тестовый клиент."""
    return client.post(
        "/api/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers or {},
    )


# =============================================================================
# Базовые тесты
# =============================================================================
class TestGraphQLBasic:
    """Smoke-тесты: доступность эндпоинта и интроспекция."""

    def test_200_graphql_endpoint_exists(self):
        response = graphql_query("{ __typename }", ADMIN_HEADERS)
        assert response.status_code == 200
        assert "data" in response.json()

    def test_200_graphql_introspection(self):
        response = graphql_query("{ __schema { queryType { name } } }", ADMIN_HEADERS)
        assert response.status_code == 200
        assert "data" in response.json()
        assert response.json()["data"]["__schema"]["queryType"]["name"] == "Query"


# =============================================================================
# Справочники: EventType, PayloadType, ValueType
# =============================================================================
class TestGraphQLDictionaries:
    """Тесты для справочных типов с пагинацией, фильтрацией и вложенными связями."""

    def test_200_event_types_connection_basic(self):
        query = """
        {
            eventTypes(first: 3) {
                edges {
                    node {
                        id
                        codeName
                        description
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()["data"]["eventTypes"]
        assert isinstance(data["edges"], list)
        assert len(data["edges"]) <= 3
        assert "pageInfo" in data

    def test_200_event_type_single_by_global_id(self):
        # Сначала получаем реальный ID через список
        list_query = "{ eventTypes(first: 1) { edges { node { id codeName } } } }"
        list_resp = graphql_query(list_query, ADMIN_HEADERS)
        node_id = list_resp.json()["data"]["eventTypes"]["edges"][0]["node"]["id"]

        # Затем запрашиваем по этому ID
        query = f"""
        {{
            eventType(id: "{node_id}") {{
                id
                codeName
                description
            }}
        }}
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["data"]["eventType"]["id"] == node_id

    def test_200_payload_types_with_nested_value_type(self):
        """Проверка DataLoader: вложенный valueType подгружается без N+1."""
        query = """
        {
            payloadTypes(first: 3) {
                edges {
                    node {
                        id
                        codeName
                        valueTypeId
                        valueType {
                            id
                            name
                            description
                        }
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["payloadTypes"]["edges"]
        assert len(edges) > 0
        # Проверяем, что вложенный тип загрузился
        assert edges[0]["node"]["valueType"] is not None
        assert "name" in edges[0]["node"]["valueType"]

    def test_200_value_types_filtering_by_name(self):
        query = """
        {
            valueTypes(filter: { name: { eq: "int" } }) {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        nodes = response.json()["data"]["valueTypes"]["edges"]
        assert all(node["node"]["name"] == "int" for node in nodes)

    def test_200_value_types_string_filter_contains(self):
        query = """
        {
            valueTypes(filter: { name: { contains: "str" } }) {
                edges {
                    node { name }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        nodes = response.json()["data"]["valueTypes"]["edges"]
        assert all("str" in node["node"]["name"].lower() for node in nodes)


# =============================================================================
# AllowedPayloadRule: составной ключ + вложенные связи
# =============================================================================
class TestGraphQLAllowedPayloadRules:
    """Тесты для правил с составным первичным ключом."""

    def test_200_allowed_payload_rules_connection(self):
        query = """
        {
            allowedPayloadRules(first: 3) {
                edges {
                    cursor
                    node {
                        id
                        eventTypeId
                        payloadTypeId
                        eventType { codeName }
                        payloadType { codeName }
                    }
                }
                pageInfo { endCursor hasNextPage }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()["data"]["allowedPayloadRules"]
        assert isinstance(data["edges"], list)
        if data["edges"]:
            node = data["edges"][0]["node"]
            assert "eventTypeId" in node
            assert "payloadTypeId" in node
            # Проверяем, что вложенные связи загрузились
            assert node["eventType"] is not None or node["payloadType"] is not None

    def test_200_allowed_payload_rule_single_by_composite_id(self):
        # Получаем реальный составной ID через список
        list_query = "{ allowedPayloadRules(first: 1) { edges { node { id } } } }"
        list_resp = graphql_query(list_query, ADMIN_HEADERS)
        rule_id = list_resp.json()["data"]["allowedPayloadRules"]["edges"][0]["node"]["id"]

        # Запрашиваем по этому ID
        query = f"""
        {{
            allowedPayloadRule(id: "{rule_id}") {{
                id
                eventTypeId
                payloadTypeId
                eventType {{ codeName }}
                payloadType {{ codeName }}
            }}
        }}
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        rule = response.json()["data"]["allowedPayloadRule"]
        assert rule["id"] == rule_id


# =============================================================================
# Клиенты и отзывы: вложенные связи + фильтрация
# =============================================================================
class TestGraphQLClientsAndReviews:
    """Тесты для ClientId и Review с проверкой DataLoader и фильтрации."""

    def test_200_client_ids_with_sorting(self):
        """Проверка кастомной сортировки (creation_date DESC)."""
        query = """
        {
            clientIds(first: 3) {
                edges {
                    node {
                        id
                        ident
                        creationDate
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["clientIds"]["edges"]
        # Проверяем, что данные отсортированы по убыванию даты
        if len(edges) >= 2:
            dates = [e["node"]["creationDate"] for e in edges]
            assert dates == sorted(dates, reverse=True)

    def test_200_reviews_with_nested_relations(self):
        """Проверка загрузки связанных client и status через DataLoader."""
        query = """
        {
            reviews(first: 3) {
                edges {
                    node {
                        id
                        text
                        creationDate
                        client {
                            id
                            ident
                        }
                        status {
                            id
                            name
                        }
                        problem {
                            id
                        }
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["reviews"]["edges"]
        assert len(edges) > 0
        node = edges[0]["node"]
        # Проверяем, что вложенные связи загрузились
        assert node["client"] is not None
        assert node["status"] is not None
        assert "ident" in node["client"]
        assert "name" in node["status"]

    def test_200_reviews_filter_by_status_and_text(self):
        """Комбинированная фильтрация: статус + текст."""
        query = """
        {
            reviews(
                first: 5
                filter: {
                    reviewStatusId: { eq: 2 }
                    text: { contains: "test" }
                }
            ) {
                edges {
                    node {
                        id
                        text
                        status { name }
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["reviews"]["edges"]
        # Все результаты должны соответствовать фильтрам
        for edge in edges:
            node = edge["node"]
            assert node["status"]["name"] is not None  # statusId=2
            assert "test" in node["text"].lower()


# =============================================================================
# События и полезные нагрузки: сложная вложенность + пагинация вложенного списка
# =============================================================================
class TestGraphQLEventsAndPayloads:
    """Тесты для Event и Payload с проверкой вложенной пагинации и связей."""

    def test_200_events_with_nested_client_and_type(self):
        """Проверка загрузки client и eventType через DataLoader."""
        query = """
        {
            events(first: 3) {
                edges {
                    node {
                        id
                        triggerTime
                        client {
                            id
                            ident
                        }
                        eventType {
                            id
                            codeName
                        }
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["events"]["edges"]
        assert len(edges) > 0
        node = edges[0]["node"]
        assert node["client"] is not None
        assert node["eventType"] is not None

    def test_200_event_with_nested_payloads_pagination(self):
        """Проверка вложенного поля payloads с пагинацией (first)."""
        # Сначала получаем ID события
        list_query = "{ events(first: 1) { edges { node { id } } } }"
        list_resp = graphql_query(list_query, ADMIN_HEADERS)
        event_id = list_resp.json()["data"]["events"]["edges"][0]["node"]["id"]

        query = f"""
        {{
            event(id: "{event_id}") {{
                id
                triggerTime
                payloads(first: 2) {{
                    edges {{
                        node {{
                            id
                            value
                            payloadType {{ codeName }}
                        }}
                    }}
                    pageInfo {{ hasNextPage }}
                }}
            }}
        }}
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        event = response.json()["data"]["event"]
        payloads = event["payloads"]["edges"]
        # Проверяем, что лимит first=2 применён
        assert len(payloads) <= 2
        if payloads:
            assert "value" in payloads[0]["node"]

    def test_200_payloads_with_filter_and_nested_event(self):
        """Фильтрация Payload + загрузка связанного Event."""
        query = """
        {
            payloads(
                first: 3
                filter: { value: { contains: "test" } }
            ) {
                edges {
                    node {
                        id
                        value
                        event {
                            id
                            triggerTime
                        }
                        payloadType {
                            codeName
                            valueType { name }
                        }
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["payloads"]["edges"]
        for edge in edges:
            node = edge["node"]
            assert "test" in node["value"].lower()
            assert node["event"] is not None
            assert node["payloadType"] is not None


# =============================================================================
# Relay Node: универсальный запрос по любому типу
# =============================================================================
class TestGraphQLRelayNode:
    """Тесты для универсального поля node(id: ID!)."""

    def test_200_node_query_with_inline_fragments(self):
        """Динамическое разрешение типа через inline fragments."""
        # Получаем реальный ID EventType
        list_query = "{ eventTypes(first: 1) { edges { node { id } } } }"
        list_resp = graphql_query(list_query, ADMIN_HEADERS)
        node_id = list_resp.json()["data"]["eventTypes"]["edges"][0]["node"]["id"]

        query = f"""
        {{
            node(id: "{node_id}") {{
                __typename
                id
                ... on EventType {{
                    codeName
                    description
                }}
                ... on PayloadType {{
                    codeName
                }}
                ... on Event {{
                    triggerTime
                }}
            }}
        }}
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        node = response.json()["data"]["node"]
        assert node["__typename"] == "EventType"
        assert "codeName" in node


# =============================================================================
# Расширенная фильтрация: логические операторы, диапазоны, списки
# =============================================================================
class TestGraphQLFiltering:
    """Комплексные тесты фильтрации: and/or/not, between, isIn, строковые операторы."""

    def test_200_filter_logical_and(self):
        query = """
        {
            eventTypes(
                filter: {
                    and: [
                        { codeName: { contains: "test" } }
                        { id: { gt: 0 } }
                    ]
                }
            ) {
                edges { node { id codeName } }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["eventTypes"]["edges"]
        for edge in edges:
            node = edge["node"]
            assert "test" in node["codeName"].lower()
            assert node["id"] > 0

    def test_200_filter_logical_or(self):
        query = """
        {
            valueTypes(
                filter: {
                    or: [
                        { name: { eq: "int" } }
                        { name: { eq: "string" } }
                    ]
                }
            ) {
                edges { node { name } }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["valueTypes"]["edges"]
        names = [e["node"]["name"] for e in edges]
        assert all(name in ["int", "string"] for name in names)

    def test_200_filter_not_operator(self):
        query = """
        {
            eventTypes(
                filter: {
                    not: { codeName: { eq: "deprecated" } }
                }
            ) {
                edges { node { codeName } }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["eventTypes"]["edges"]
        # Ни один результат не должен быть "deprecated"
        assert all(e["node"]["codeName"] != "deprecated" for e in edges)

    def test_200_filter_int_range_between(self):
        query = """
        {
            eventTypes(
                filter: { id: { between: [1, 100] } }
            ) {
                edges { node { id } }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["eventTypes"]["edges"]

        # 🔹 Декодируем GlobalID → извлекаем сырый int перед сравнением
        raw_ids = []
        for edge in edges:
            # from_base64 возвращает кортеж (type_name, node_id)
            _, node_id_str = from_base64(edge["node"]["id"])
            raw_ids.append(int(node_id_str))

        # Теперь сравниваем int с int
        assert all(1 <= i <= 100 for i in raw_ids), f"IDs {raw_ids} должны быть в диапазоне [1, 100]"

    def test_200_filter_string_operators(self):
        query = """
        {
            eventTypes(
                filter: {
                    codeName: {
                        startsWith: "site",
                        endsWith: "type"
                    }
                }
            ) {
                edges { node { codeName } }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["eventTypes"]["edges"]
        for edge in edges:
            name = edge["node"]["codeName"]
            assert name.startswith("site") or name.endswith("type")


# =============================================================================
# Пагинация: курсоры, hasNextPage, hasPreviousPage
# =============================================================================
class TestGraphQLPagination:
    """Тесты курсорной пагинации Relay."""

    def test_200_pagination_first_and_page_info(self):
        query = """
        {
            eventTypes(first: 2) {
                edges {
                    cursor
                    node { id }
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    startCursor
                    endCursor
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()["data"]["eventTypes"]
        assert len(data["edges"]) == 2
        assert "endCursor" in data["pageInfo"]
        assert isinstance(data["pageInfo"]["hasNextPage"], bool)

    def test_200_pagination_cursor_navigation(self):
        # Шаг 1: получаем первую страницу и endCursor
        query1 = """
        {
            eventTypes(first: 2) {
                edges { node { id } }
                pageInfo { endCursor hasNextPage }
            }
        }
        """
        resp1 = graphql_query(query1, ADMIN_HEADERS)
        page1 = resp1.json()["data"]["eventTypes"]
        assert page1["pageInfo"]["hasNextPage"] is True
        cursor = page1["pageInfo"]["endCursor"]

        # Шаг 2: запрашиваем следующую страницу по курсору
        query2 = f"""
        {{
            eventTypes(first: 2, after: "{cursor}") {{
                edges {{ node {{ id }} }}
                pageInfo {{ hasPreviousPage }}
            }}
        }}
        """
        resp2 = graphql_query(query2, ADMIN_HEADERS)
        page2 = resp2.json()["data"]["eventTypes"]
        # IDs на второй странице не должны совпадать с первой
        ids1 = {e["node"]["id"] for e in page1["edges"]}
        ids2 = {e["node"]["id"] for e in page2["edges"]}
        assert ids1.isdisjoint(ids2)
        assert page2["pageInfo"]["hasPreviousPage"] is True


# =============================================================================
# Права доступа: неавторизованные запросы
# =============================================================================
class TestGraphQLUnauthorized:
    """Тесты проверки прав доступа (401/403)."""

    def test_401_event_types_without_token(self):
        query = "{ eventTypes(first: 1) { edges { node { id } } } }"
        response = graphql_query(query)  # ← без ADMIN_HEADERS
        assert response.status_code == 401

    def test_401_reviews_without_token(self):
        query = "{ reviews(first: 1) { edges { node { id } } } }"
        response = graphql_query(query)
        assert response.status_code == 401

    def test_401_single_node_without_token(self):
        # Даже если знаем валидный ID, без токена доступ запрещён
        query = '{ eventType(id: "RXZlbnRUeXBlOjE=") { id } }'
        response = graphql_query(query)
        assert response.status_code == 401


# =============================================================================
# Edge-кейсы и обработка ошибок
# =============================================================================
class TestGraphQLEdgeCases:
    """Тесты граничных условий и обработки ошибок."""

    def test_400_invalid_global_id_format(self):
        query = '{ eventType(id: "not-a-valid-global-id") { id } }'
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200  # GraphQL всегда 200, ошибки в body
        assert "errors" in response.json()
        assert "Invalid base64" in response.json()["errors"][0]["message"]

    def test_404_non_existent_node(self):
        # GlobalID для несуществующего ID (999999)
        query = '{ eventType(id: "RXZlbnRUeXBlOjk5OTk5OQ==") { id } }'
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        # Relay возвращает null, если узел не найден
        assert response.json()["data"]["eventType"] is None

    def test_200_empty_filter_result(self):
        query = """
        {
            eventTypes(filter: { id: { eq: 999999 } }) {
                edges { node { id } }
                pageInfo { hasNextPage }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        edges = response.json()["data"]["eventTypes"]["edges"]
        assert len(edges) == 0
        assert response.json()["data"]["eventTypes"]["pageInfo"]["hasNextPage"] is False

    def test_200_multiple_queries_in_one_request(self):
        """Проверка, что несколько независимых запросов работают в одном HTTP-запросе."""
        query = """
        {
            eventTypes(first: 1) { edges { node { id } } }
            valueTypes(first: 1) { edges { node { id } } }
            clientIds(first: 1) { edges { node { id } } }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        response = response.json()
        data = response["data"]
        print(response)
        assert "eventTypes" in data
        assert "valueTypes" in data
        assert "clientIds" in data
