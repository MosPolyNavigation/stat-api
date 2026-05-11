"""Integration tests for GraphQL Query operations in event_system domain."""
import pytest

from tests.graphql.base import (
    graphql_query
)

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


# =============================================================================
# Базовые тесты
# =============================================================================
class TestGraphQLBasic:
    """Smoke-тесты: доступность эндпоинта и интроспекция."""

    def test_200_graphql_endpoint_exists(self):
        response = graphql_query("{ __typename }", headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        assert "data" in response["data"]

    def test_200_graphql_introspection(self):
        response = graphql_query("{ __schema { queryType { name } } }", headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        assert "data" in response["data"]
        assert response["data"]["data"]["__schema"]["queryType"]["name"] == "Query"


# =============================================================================
# Справочники: EventType, PayloadType, ValueType
# =============================================================================
class TestGraphQLDictionaries:
    """Тесты для справочных типов с пагинацией, фильтрацией и вложенными связями."""

    def test_200_event_types_connection_basic(self):
        query = """
        {
            eventTypes(pagination: { page: 1, pageSize: 3 }) {
                nodes {
                    id
                    codeName
                    description
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
                paginationInfo {
                    totalCount
                    currentPage
                }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        data = response["data"]["data"]["eventTypes"]
        assert isinstance(data["nodes"], list)
        assert len(data["nodes"]) <= 3
        assert "pageInfo" in data
        assert "paginationInfo" in data

    def test_200_event_type_single_by_id(self):
        # Сначала получаем реальный ID через список
        list_query = "{ eventTypes(pagination: { pageSize: 1 }) { nodes { id codeName } } }"
        list_resp = graphql_query(list_query, headers=ADMIN_HEADERS)["data"]
        node_id = list_resp["data"]["eventTypes"]["nodes"][0]["id"]

        # Затем запрашиваем по этому ID (простой Int, не GlobalID)
        query = f"""
        {{
            eventType(id: {node_id}) {{
                id
                codeName
                description
            }}
        }}
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        assert response["data"]["data"]["eventType"]["id"] == node_id

    def test_200_payload_types_with_nested_value_type(self):
        """Проверка DataLoader: вложенный valueType подгружается без N+1."""
        query = """
        {
            payloadTypes(pagination: { pageSize: 3 }) {
                nodes {
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
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["payloadTypes"]["nodes"]
        assert len(nodes) > 0
        assert nodes[0]["valueType"] is not None
        assert "name" in nodes[0]["valueType"]

    def test_200_value_types_filtering_by_name(self):
        query = """
        {
            valueTypes(filter: { name: { eq: "int" } }) {
                nodes { id name }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["valueTypes"]["nodes"]
        assert all(node["name"] == "int" for node in nodes)

    def test_200_value_types_string_filter_contains(self):
        query = """
        {
            valueTypes(filter: { name: { contains: "str" } }) {
                nodes { name }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["valueTypes"]["nodes"]
        assert all("str" in node["name"].lower() for node in nodes)


# =============================================================================
# AllowedPayloadRule: составной ключ + вложенные связи
# =============================================================================
class TestGraphQLAllowedPayloadRules:
    """Тесты для правил с составным первичным ключом."""

    def test_200_allowed_payload_rules_connection(self):
        query = """
        {
            allowedPayloadRules(pagination: { pageSize: 3 }) {
                nodes {
                    eventTypeId
                    payloadTypeId
                    eventType { codeName }
                    payloadType { codeName }
                }
                pageInfo { hasNextPage endCursor }
                paginationInfo { totalCount currentPage }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        data = response["data"]["data"]["allowedPayloadRules"]
        assert isinstance(data["nodes"], list)
        if data["nodes"]:
            node = data["nodes"][0]
            assert "eventTypeId" in node
            assert "payloadTypeId" in node
            assert node["eventType"] is not None or node["payloadType"] is not None

    def test_200_allowed_payload_rule_single_by_composite_key(self):
        # Получаем реальные ключи через список
        list_query = "{ allowedPayloadRules(pagination: { pageSize: 1 }) { nodes { eventTypeId payloadTypeId } } }"
        list_resp = graphql_query(list_query, headers=ADMIN_HEADERS)["data"]
        rule = list_resp["data"]["allowedPayloadRules"]["nodes"][0]

        # Запрашиваем по составному ключу (два Int аргумента)
        query = f"""
        {{
            allowedPayloadRule(eventTypeId: {rule["eventTypeId"]}, payloadTypeId: {rule["payloadTypeId"]}) {{
                eventTypeId
                payloadTypeId
                eventType {{ codeName }}
                payloadType {{ codeName }}
            }}
        }}
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        result = response["data"]["data"]["allowedPayloadRule"]
        assert result["eventTypeId"] == rule["eventTypeId"]
        assert result["payloadTypeId"] == rule["payloadTypeId"]


# =============================================================================
# Клиенты и отзывы: вложенные связи + фильтрация
# =============================================================================
class TestGraphQLClientsAndReviews:
    """Тесты для ClientId и Review с проверкой DataLoader и фильтрации."""

    def test_200_client_ids_with_sorting(self):
        """Проверка кастомной сортировки (creation_date DESC)."""
        query = """
        {
            clientIds(
                pagination: { pageSize: 3 }
                orderBy: { creationDate: DESC }
            ) {
                nodes {
                    id
                    ident
                    creationDate
                }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["clientIds"]["nodes"]
        if len(nodes) >= 2:
            dates = [n["creationDate"] for n in nodes]
            assert dates == sorted(dates, reverse=True)

    def test_200_reviews_with_nested_relations(self):
        """Проверка загрузки связанных client и status через DataLoader."""
        query = """
        {
            reviews(pagination: { pageSize: 3 }) {
                nodes {
                    id
                    text
                    creationDate
                    client { id ident }
                    status { id name }
                    problem { id }
                }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["reviews"]["nodes"]
        assert len(nodes) > 0
        node = nodes[0]
        assert node["client"] is not None and "ident" in node["client"]
        assert node["status"] is not None and "name" in node["status"]

    def test_200_reviews_filter_by_status_and_text(self):
        """Комбинированная фильтрация: статус + текст."""
        query = """
        {
            reviews(
                pagination: { pageSize: 5 }
                filter: {
                    reviewStatusId: { eq: 2 }
                    text: { contains: "test" }
                }
            ) {
                nodes { id text status { name } }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["reviews"]["nodes"]
        for node in nodes:
            assert node["status"]["name"] is not None
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
            events(pagination: { pageSize: 3 }) {
                nodes {
                    id
                    triggerTime
                    client { id ident }
                    eventType { id codeName }
                }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["events"]["nodes"]
        assert len(nodes) > 0
        node = nodes[0]
        assert node["client"] is not None
        assert node["eventType"] is not None

    def test_200_event_with_nested_payloads_pagination(self):
        """Проверка вложенного поля payloads с пагинацией."""
        # Сначала получаем ID события
        list_query = "{ events(pagination: { pageSize: 1 }) { nodes { id } } }"
        list_resp = graphql_query(list_query, headers=ADMIN_HEADERS)["data"]
        event_id = list_resp["data"]["events"]["nodes"][0]["id"]

        query = f"""
        {{
            event(id: {event_id}) {{
                id
                triggerTime
                payloads(first: 2) {{
                    id value payloadType {{ codeName }}
                }}
            }}
        }}
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        event = response["data"]["data"]["event"]
        payloads = event["payloads"]
        assert len(payloads) <= 2
        if payloads:
            assert "value" in payloads[0]

    def test_200_payloads_with_filter_and_nested_event(self):
        """Фильтрация Payload + загрузка связанного Event."""
        query = """
        {
            payloads(
                pagination: { pageSize: 3 }
                filter: { value: { contains: "test" } }
            ) {
                nodes {
                    id
                    value
                    event { id triggerTime }
                    payloadType { codeName valueType { name } }
                }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["payloads"]["nodes"]
        for node in nodes:
            assert "test" in node["value"].lower()
            assert node["event"] is not None
            assert node["payloadType"] is not None


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
            ) { nodes { id codeName } }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["eventTypes"]["nodes"]
        for node in nodes:
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
            ) { nodes { name } }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["valueTypes"]["nodes"]
        names = [n["name"] for n in nodes]
        assert all(name in ["int", "string"] for name in names)

    def test_200_filter_not_operator(self):
        query = """
        {
            eventTypes(
                filter: { not: { codeName: { eq: "deprecated" } } }
            ) { nodes { codeName } }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["eventTypes"]["nodes"]
        assert all(n["codeName"] != "deprecated" for n in nodes)

    def test_200_filter_int_range_between(self):
        query = """
        {
            eventTypes(filter: { id: { between: [1, 100] } }) {
                nodes { id }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["eventTypes"]["nodes"]
        ids = [n["id"] for n in nodes]
        assert all(1 <= i <= 100 for i in ids), f"IDs {ids} должны быть в диапазоне [1, 100]"

    def test_200_filter_string_operators(self):
        query = """
        {
            eventTypes(
                filter: {
                    codeName: { startsWith: "site", endsWith: "type" }
                }
            ) { nodes { codeName } }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["eventTypes"]["nodes"]
        for node in nodes:
            name = node["codeName"]
            assert name.startswith("site") or name.endswith("type")


# =============================================================================
# Пагинация: page/pageSize, hasNextPage, totalCount
# =============================================================================
class TestGraphQLPagination:
    """Тесты кастомной offset-пагинации."""

    def test_200_pagination_page_and_info(self):
        query = """
        {
            eventTypes(pagination: { page: 1, pageSize: 2 }) {
                nodes { id }
                pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        data = response["data"]["data"]["eventTypes"]
        assert len(data["nodes"]) <= 2
        assert "paginationInfo" in data
        assert data["paginationInfo"]["currentPage"] == 1

    def test_200_pagination_navigation(self):
        # Шаг 1: первая страница
        query1 = """
        {
            eventTypes(pagination: { page: 1, pageSize: 2 }) {
                nodes { id }
                pageInfo { hasNextPage }
                paginationInfo { totalPages }
            }
        }
        """
        resp1 = graphql_query(query1, headers=ADMIN_HEADERS)["data"]
        page1 = resp1["data"]["eventTypes"]
        ids1 = {n["id"] for n in page1["nodes"]}

        # Шаг 2: вторая страница (если есть)
        if page1["pageInfo"]["hasNextPage"]:
            query2 = """
            {
                eventTypes(pagination: { page: 2, pageSize: 2 }) {
                    nodes { id }
                    pageInfo { hasPreviousPage }
                }
            }
            """
            resp2 = graphql_query(query2, headers=ADMIN_HEADERS)["data"]
            page2 = resp2["data"]["eventTypes"]
            ids2 = {n["id"] for n in page2["nodes"]}
            # IDs на разных страницах не должны пересекаться
            assert ids1.isdisjoint(ids2)
            assert page2["pageInfo"]["hasPreviousPage"] is True


# =============================================================================
# Права доступа: неавторизованные запросы
# =============================================================================
class TestGraphQLUnauthorized:
    """Тесты проверки прав доступа (401/403)."""

    def test_401_event_types_without_token(self):
        query = "{ eventTypes(pagination: { pageSize: 1 }) { nodes { id } } }"
        response = graphql_query(query)
        assert response["status_code"] == 401

    def test_401_reviews_without_token(self):
        query = "{ reviews(pagination: { pageSize: 1 }) { nodes { id } } }"
        response = graphql_query(query)
        assert response["status_code"] == 401

    def test_401_single_node_without_token(self):
        query = '{ eventType(id: 1) { id } }'
        response = graphql_query(query)
        assert response["status_code"] == 401


# =============================================================================
# Edge-кейсы и обработка ошибок
# =============================================================================
class TestGraphQLEdgeCases:
    """Тесты граничных условий и обработки ошибок."""

    def test_400_invalid_id_format(self):
        # Простой Int ID, не строка
        query = '{ eventType(id: "not-an-int") { id } }'
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        assert "errors" in response["data"]

    def test_404_non_existent_node(self):
        query = '{ eventType(id: 999999) { id } }'
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        assert response["data"]["data"]["eventType"] is None

    def test_200_empty_filter_result(self):
        query = """
        {
            eventTypes(filter: { id: { eq: 999999 } }) {
                nodes { id }
                pageInfo { hasNextPage }
                paginationInfo { totalCount }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        nodes = response["data"]["data"]["eventTypes"]["nodes"]
        assert len(nodes) == 0
        assert response["data"]["data"]["eventTypes"]["paginationInfo"]["totalCount"] == 0

    def test_200_multiple_queries_in_one_request(self):
        query = """
        {
            eventTypes(pagination: { pageSize: 1 }) { nodes { id } }
            valueTypes(pagination: { pageSize: 1 }) { nodes { id } }
            clientIds(pagination: { pageSize: 1 }) { nodes { id } }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        assert response["status_code"] == 200
        data = response["data"]["data"]
        assert "eventTypes" in data
        assert "valueTypes" in data
        assert "clientIds" in data


# =============================================================================
# Dashboard Query Tests
# =============================================================================
class TestGraphQLDashboardQuery:
    """Тесты для запросов Dashboard и DashboardType."""

    def test_200_dashboard_types_connection(self):
        query = """
        {
            dashboardTypes(pagination: { pageSize: 3 }) {
                nodes { id codeName description }
                pageInfo { hasNextPage endCursor }
                paginationInfo { totalCount currentPage }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        data = resp["data"]["dashboardTypes"]
        assert isinstance(data["nodes"], list)
        if data["nodes"]:
            assert "codeName" in data["nodes"][0]

    def test_200_dashboard_type_by_id(self):
        list_resp = graphql_query(
            "{ dashboardTypes(pagination: { pageSize: 1 }) { nodes { id } } }",
            headers=ADMIN_HEADERS
        )["data"]
        dt_id = list_resp["data"]["dashboardTypes"]["nodes"][0]["id"]
        query = f'{{ dashboardType(id: {dt_id}) {{ id codeName }} }}'
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        assert resp["data"]["dashboardType"]["id"] == dt_id

    def test_200_dashboards_with_filter(self):
        # Создаём тестовый дашборд
        create_resp = graphql_query("""
        mutation {
            createDashboard(data: {
                displayOrder: 999, eventTypeId: 1, dashboardTypeId: 1,
                titleText: "test-query-dashboard"
            }) { id }
        }
        """, headers=ADMIN_HEADERS)["data"]

        if "errors" not in create_resp:
            dashboard_id = create_resp["data"]["createDashboard"]["id"]
            try:
                query = """
                {
                    dashboards(
                        pagination: { pageSize: 5 }
                        filter: { dashboardTypeId: { eq: 1 } }
                    ) {
                        nodes { id titleText displayOrder eventType { codeName } }
                        paginationInfo { totalCount }
                    }
                }
                """
                resp = graphql_query(query, headers=ADMIN_HEADERS)
                assert resp["status_code"] == 200
                resp = resp["data"]
                nodes = resp["data"]["dashboards"]["nodes"]
                titles = [n["titleText"] for n in nodes]
                assert "test-query-dashboard" in titles
            finally:
                graphql_query(f'mutation {{ deleteDashboard(id: {dashboard_id}) }}', headers=ADMIN_HEADERS)

    def test_200_dashboards_with_filter_and_pagination(self):
        query = """
        {
            dashboards(
                pagination: { page: 1, pageSize: 2 }
                filter: { titleText: { contains: "test" }, dashboardTypeId: { eq: 1 } }
            ) {
                nodes { id titleText }
                pageInfo { hasNextPage }
                paginationInfo { currentPage totalPages }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        data = resp["data"]["dashboards"]
        for node in data["nodes"]:
            assert "test" in node["titleText"].lower()
        assert len(data["nodes"]) <= 2

    def test_200_dashboard_single_by_id(self):
        list_resp = graphql_query(
            "{ dashboards(pagination: { pageSize: 1 }, filter: { dashboardTypeId: { eq: 1 } }) { nodes { id } } }",
            headers=ADMIN_HEADERS
        )["data"]
        nodes = list_resp["data"]["dashboards"]["nodes"]
        if not nodes:
            pytest.skip("No dashboards in test DB")
        dash_id = nodes[0]["id"]
        query = f'{{ dashboard(id: {dash_id}) {{ id titleText eventType {{ codeName }} }} }}'
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        dash = resp["data"]["dashboard"]
        assert dash["id"] == dash_id
        assert "titleText" in dash


# =============================================================================
# Тесты для ReviewStatus (справочник статусов)
# =============================================================================
class TestReviewStatusQueries:
    """Тесты для GraphQL query операций со статусами отзывов."""

    def test_200_review_statuses_success(self):
        """Успешное получение списка статусов."""
        query = """
        {
            reviewStatuses(pagination: { page: 1, pageSize: 10 }) {
                nodes { id name }
                paginationInfo { totalCount }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        data = resp["data"]["data"]["reviewStatuses"]
        assert isinstance(data["nodes"], list)
        assert data["paginationInfo"]["totalCount"] > 0

    def test_200_review_status_single_by_id(self):
        """Получение одного статуса по ID."""
        query = """
        {
            reviewStatus(id: 1) { id name }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        status = resp["data"]["data"]["reviewStatus"]
        assert status is not None
        assert "id" in status
        assert "name" in status

    def test_200_review_status_nested_reviews(self):
        """Проверка вложенного поля reviews."""
        query = """
        {
            reviewStatus(id: 1) {
                id
                name
                reviews(first: 2) {
                    id
                    text
                }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        status = resp["data"]["data"]["reviewStatus"]
        assert status is not None
        # Проверяем, что массив reviews вернулся (даже если пустой)
        assert "reviews" in status
        assert isinstance(status["reviews"], list)

    def test_200_review_status_ordering(self):
        """Проверка сортировки статусов по имени."""
        query = """
        {
            reviewStatuses(orderBy: { name: ASC }) {
                nodes { id name }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        print(resp)
        assert resp["status_code"] == 200
        nodes = resp["data"]["data"]["reviewStatuses"]["nodes"]
        names = [n["name"] for n in nodes]
        assert names == sorted(names)
