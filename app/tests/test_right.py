"""Тесты для GraphQL эндпоинтов управления правами (Right)"""

import pytest
from .base import client

# Токен администратора из base.py
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

# GraphQL endpoint
GRAPHQL_ENDPOINT = "/api/graphql"


def graphql_query(query, variables=None, headers=None):
    """Хелпер для выполнения GraphQL запросов."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = client.post(
        GRAPHQL_ENDPOINT,
        headers=headers or {},
        json=payload
    )
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    }


def assert_graphql_success(response, field_name):
    """Проверяет успешный GraphQL ответ без ошибок"""
    assert response["status_code"] == 200
    assert "errors" not in response["data"] or not response["data"].get("errors")
    assert response["data"].get("data") is not None
    assert response["data"]["data"].get(field_name) is not None
    return response["data"]["data"][field_name]


def assert_graphql_error(response, error_substring):
    """Проверяет наличие GraphQL ошибки с ожидаемым текстом"""
    assert response["status_code"] == 200
    assert "errors" in response["data"]
    assert len(response["data"]["errors"]) > 0
    error_message = response["data"]["errors"][0]["message"].lower()
    assert error_substring.lower() in error_message
    return response["data"]["errors"][0]


class TestRightQueries:
    """Тесты для GraphQL query операций с правами"""

    def test_rights_query_success(self):
        """Успешное получение списка прав с пагинацией"""
        query = """
        query GetRights($pagination: PaginationInput, $filter: RightFilterInput) {
            rights(pagination: $pagination, filter: $filter) {
                nodes {
                    id
                    name
                }
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    startCursor
                    endCursor
                }
                paginationInfo {
                    totalCount
                    currentPage
                    totalPages
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filter": None
            },
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "rights")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) == 4  # view, create, edit, delete
        assert result["paginationInfo"]["totalCount"] == 4

    def test_rights_query_with_filter_id(self):
        """Фильтрация прав по id"""
        query = """
        query GetRights($filter: RightFilterInput) {
            rights(filter: $filter) {
                nodes {
                    id
                    name
                }
            }
        }
        """

        response = graphql_query(
            query,
            variables={"filter": {"id": 1}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "rights")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == 1
        assert result["nodes"][0]["name"] == "view"

    def test_rights_query_with_filter_name(self):
        """Фильтрация прав по name"""
        query = """
        query GetRights($filter: RightFilterInput) {
            rights(filter: $filter) {
                nodes {
                    id
                    name
                }
            }
        }
        """

        response = graphql_query(
            query,
            variables={"filter": {"name": "create"}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "rights")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "create"

    def test_rights_query_pagination(self):
        """Проверка пагинации прав"""
        query = """
        query GetRights($pagination: PaginationInput) {
            rights(pagination: $pagination) {
                nodes {
                    id
                    name
                }
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                    startCursor
                    endCursor
                }
                paginationInfo {
                    totalCount
                    currentPage
                    totalPages
                }
            }
        }
        """

        # Первая страница (limit=2)
        response1 = graphql_query(
            query,
            variables={"pagination": {"limit": 2, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "rights")

        # Вторая страница
        response2 = graphql_query(
            query,
            variables={"pagination": {"limit": 2, "offset": 2}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "rights")

        # Проверяем что данные разные
        assert result1["nodes"][0]["id"] != result2["nodes"][0]["id"]

        # Проверяем pageInfo
        assert result1["pageInfo"]["hasPreviousPage"] is False
        assert result1["pageInfo"]["hasNextPage"] is True

    def test_rights_query_all_expected_rights_exist(self):
        """Проверка что все ожидаемые права существуют"""
        query = """
        query GetRights {
            rights(pagination: {limit: 10}) {
                nodes {
                    id
                    name
                }
            }
        }
        """

        response = graphql_query(query, headers=ADMIN_HEADERS)
        result = assert_graphql_success(response, "rights")

        # Проверяем наличие всех прав
        rights_map = {r["id"]: r["name"] for r in result["nodes"]}

        assert rights_map.get(1) == "view"
        assert rights_map.get(2) == "create"
        assert rights_map.get(3) == "edit"
        assert rights_map.get(4) == "delete"

    def test_rights_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр ролей"""
        # Создаём пользователя без прав
        import uuid
        test_login = f"noperms_{uuid.uuid4().hex[:8]}"
        
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        
        # Получаем токен пользователя
        token_response = client.post(
            "/api/auth/token",
            data={"username": test_login, "password": "pass123"}
        )
        user_token = token_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Пытаемся получить список прав
        query = """
        query GetRights {
            rights(pagination: {limit: 10}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        
        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")
