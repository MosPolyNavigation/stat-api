"""Тесты для GraphQL эндпоинтов управления целями (Goal)"""

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


class TestGoalQueries:
    """Тесты для GraphQL query операций с целями"""

    def test_goals_query_success(self):
        """Успешное получение списка целей с пагинацией"""
        query = """
        query GetGoals($pagination: PaginationInput, $filter: GoalFilterInput) {
            goals(pagination: $pagination, filter: $filter) {
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
        
        result = assert_graphql_success(response, "goals")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) >= 8  # Минимум 8 целей по умолчанию
        assert result["paginationInfo"]["totalCount"] >= 8

    def test_goals_query_with_filter_id(self):
        """Фильтрация целей по id"""
        query = """
        query GetGoals($filter: GoalFilterInput) {
            goals(filter: $filter) {
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
        
        result = assert_graphql_success(response, "goals")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == 1
        assert result["nodes"][0]["name"] == "stats"

    def test_goals_query_with_filter_name(self):
        """Фильтрация целей по name"""
        query = """
        query GetGoals($filter: GoalFilterInput) {
            goals(filter: $filter) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"filter": {"name": "users"}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "goals")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "users"

    def test_goals_query_pagination(self):
        """Проверка пагинации целей"""
        query = """
        query GetGoals($pagination: PaginationInput) {
            goals(pagination: $pagination) {
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
        
        # Первая страница (limit=3)
        response1 = graphql_query(
            query,
            variables={"pagination": {"limit": 3, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "goals")
        
        # Вторая страница
        response2 = graphql_query(
            query,
            variables={"pagination": {"limit": 3, "offset": 3}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "goals")
        
        # Проверяем что данные разные
        if len(result1["nodes"]) > 0 and len(result2["nodes"]) > 0:
            assert result1["nodes"][0]["id"] != result2["nodes"][0]["id"]
        
        # Проверяем pageInfo
        assert result1["pageInfo"]["hasPreviousPage"] is False

    def test_goals_query_all_expected_goals_exist(self):
        """Проверка что все ожидаемые цели существуют"""
        query = """
        query GetGoals {
            goals(pagination: {limit: 20}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        
        response = graphql_query(query, headers=ADMIN_HEADERS)
        result = assert_graphql_success(response, "goals")
        
        # Проверяем наличие основных целей
        goals_map = {g["id"]: g["name"] for g in result["nodes"]}
        
        assert goals_map.get(1) == "stats"
        assert goals_map.get(3) == "users"
        assert goals_map.get(4) == "roles"
        assert goals_map.get(8) == "nav_data"

    def test_goals_query_with_user_pass_goal(self):
        """Проверка что цель user_pass существует (ID: 9)"""
        query = """
        query GetGoals($filter: GoalFilterInput) {
            goals(filter: $filter) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"filter": {"id": 9}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "goals")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "user_pass"

    def test_goals_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр ролей"""
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
        
        # Пытаемся получить список целей
        query = """
        query GetGoals {
            goals(pagination: {limit: 10}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        
        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")

    def test_goals_query_pagination_info_accuracy(self):
        """Проверка точности paginationInfo для целей"""
        query = """
        query GetGoals($pagination: PaginationInput) {
            goals(pagination: $pagination) {
                nodes {
                    id
                }
                paginationInfo {
                    totalCount
                    currentPage
                    totalPages
                }
            }
        }
        """
        
        # Запрос с limit=1
        response1 = graphql_query(
            query,
            variables={"pagination": {"limit": 1, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "goals")
        
        # Запрос с limit=10
        response2 = graphql_query(
            query,
            variables={"pagination": {"limit": 10, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "goals")
        
        # totalCount должен быть одинаковым
        assert result1["paginationInfo"]["totalCount"] == result2["paginationInfo"]["totalCount"]
