"""Тесты для GraphQL эндпоинтов управления связями роль-право-цель"""

import pytest
import uuid
from .base import client

# Токен администратора из base.py (пользователь с полными правами)
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

# GraphQL endpoint
GRAPHQL_ENDPOINT = "/api/graphql"


def graphql_query(query, variables=None, headers=None):
    """
    Хелпер для выполнения GraphQL запросов.
    
    Args:
        query: GraphQL query/mutation строка
        variables: Переменные для запроса (dict)
        headers: HTTP заголовки
    
    Returns:
        dict с данными из response.json()
    """
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
    assert error_substring.lower() in error_message, f"Ожидалось '{error_substring}' в '{error_message}'"
    return response["data"]["errors"][0]


class TestRoleRightGoalQueries:
    """Тесты для GraphQL query операций с role_right_goal"""

    def test_role_right_goals_query_success(self):
        """Успешное получение списка связей роль-право-цель с пагинацией"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput, $filter: RoleRightGoalFilterInput) {
            roleRightGoals(pagination: $pagination, filter: $filter) {
                nodes {
                    roleId
                    rightId
                    goalId
                    role {
                        id
                        name
                    }
                    right {
                        id
                        name
                    }
                    goal {
                        id
                        name
                    }
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
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) > 0  # У admin роли должны быть связи
        assert result["paginationInfo"]["totalCount"] >= 1

    def test_role_right_goals_query_with_filter_role_id(self):
        """Фильтрация связей по role_id"""
        # Получаем ID admin роли
        roles_query = """
        query GetRoles {
            roles(pagination: {limit: 1}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        roles_response = graphql_query(roles_query, headers=ADMIN_HEADERS)
        admin_id = roles_response["data"]["data"]["roles"]["nodes"][0]["id"]
        
        # Фильтруем по role_id
        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) {
                nodes {
                    roleId
                    rightId
                    goalId
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"filter": {"roleId": admin_id}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        assert all(rrg["roleId"] == admin_id for rrg in result["nodes"])

    def test_role_right_goals_query_with_filter_right_id(self):
        """Фильтрация связей по right_id"""
        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) {
                nodes {
                    roleId
                    rightId
                    goalId
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"filter": {"rightId": 1}},  # view right
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        assert all(rrg["rightId"] == 1 for rrg in result["nodes"])

    def test_role_right_goals_query_with_filter_goal_id(self):
        """Фильтрация связей по goal_id"""
        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) {
                nodes {
                    roleId
                    rightId
                    goalId
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"filter": {"goalId": 1}},  # stats goal
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        assert all(rrg["goalId"] == 1 for rrg in result["nodes"])

    def test_role_right_goals_query_with_combined_filters(self):
        """Фильтрация связей по нескольким полям одновременно"""
        # Получаем ID admin роли
        roles_query = """
        query GetRoles {
            roles(pagination: {limit: 1}) {
                nodes {
                    id
                }
            }
        }
        """
        roles_response = graphql_query(roles_query, headers=ADMIN_HEADERS)
        admin_id = roles_response["data"]["data"]["roles"]["nodes"][0]["id"]
        
        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) {
                nodes {
                    roleId
                    rightId
                    goalId
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"filter": {"roleId": admin_id, "rightId": 1}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert all(rrg["roleId"] == admin_id and rrg["rightId"] == 1 for rrg in result["nodes"])

    def test_role_right_goals_query_pagination(self):
        """Проверка пагинации связей"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes {
                    roleId
                    rightId
                    goalId
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
        
        # Первая страница
        response1 = graphql_query(
            query,
            variables={"pagination": {"limit": 5, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "roleRightGoals")
        
        # Вторая страница
        response2 = graphql_query(
            query,
            variables={"pagination": {"limit": 5, "offset": 5}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "roleRightGoals")
        
        # Проверяем pageInfo
        assert "hasPreviousPage" in result1["pageInfo"]
        assert "hasNextPage" in result1["pageInfo"]
        assert result1["pageInfo"]["hasPreviousPage"] is False  # Первая страница
        
        # Проверяем что данные разные (если есть больше 5 записей)
        if len(result1["nodes"]) == 5 and len(result2["nodes"]) > 0:
            assert result1["nodes"][0] != result2["nodes"][0]

    def test_role_right_goal_query_success(self):
        """Успешное получение конкретной связи"""
        # Получаем первую связь
        list_query = """
        query GetRoleRightGoals {
            roleRightGoals(pagination: {limit: 1}) {
                nodes {
                    roleId
                    rightId
                    goalId
                }
            }
        }
        """
        list_response = graphql_query(list_query, headers=ADMIN_HEADERS)
        first_rrg = list_response["data"]["data"]["roleRightGoals"]["nodes"][0]
        
        # Получаем конкретную связь
        query = """
        query GetRoleRightGoal($roleId: Int!, $rightId: Int!, $goalId: Int!) {
            roleRightGoal(roleId: $roleId, rightId: $rightId, goalId: $goalId) {
                roleId
                rightId
                goalId
                role {
                    id
                    name
                }
                right {
                    id
                    name
                }
                goal {
                    id
                    name
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={
                "roleId": first_rrg["roleId"],
                "rightId": first_rrg["rightId"],
                "goalId": first_rrg["goalId"]
            },
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoal")
        assert result["roleId"] == first_rrg["roleId"]
        assert result["rightId"] == first_rrg["rightId"]
        assert result["goalId"] == first_rrg["goalId"]
        assert result["role"] is not None
        assert result["right"] is not None
        assert result["goal"] is not None

    def test_role_right_goal_query_not_found(self):
        """Связь не найдена"""
        query = """
        query GetRoleRightGoal($roleId: Int!, $rightId: Int!, $goalId: Int!) {
            roleRightGoal(roleId: $roleId, rightId: $rightId, goalId: $goalId) {
                roleId
                rightId
                goalId
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"roleId": 999, "rightId": 999, "goalId": 999},
            headers=ADMIN_HEADERS
        )
        
        # GraphQL возвращает null для не найденного объекта
        assert response["status_code"] == 200
        assert response["data"]["data"]["roleRightGoal"] is None

    def test_role_right_goals_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр ролей"""
        # Создаём пользователя без прав
        test_login = f"noperms_{uuid.uuid4().hex[:8]}"
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        create_response = graphql_query(
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
        
        # Пытаемся получить список связей
        query = """
        query GetRoleRightGoals {
            roleRightGoals(pagination: {limit: 10}) {
                nodes {
                    roleId
                    rightId
                    goalId
                }
            }
        }
        """
        
        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")

    def test_role_right_goals_query_returns_related_data(self):
        """Проверка что возвращаются связанные данные (role, right, goal)"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes {
                    roleId
                    rightId
                    goalId
                    role {
                        id
                        name
                    }
                    right {
                        id
                        name
                    }
                    goal {
                        id
                        name
                    }
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"pagination": {"limit": 5, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        
        # Проверяем что все связанные данные присутствуют
        for rrg in result["nodes"]:
            assert rrg["role"] is not None
            assert "id" in rrg["role"]
            assert "name" in rrg["role"]
            
            assert rrg["right"] is not None
            assert "id" in rrg["right"]
            assert "name" in rrg["right"]
            
            assert rrg["goal"] is not None
            assert "id" in rrg["goal"]
            assert "name" in rrg["goal"]

    def test_role_right_goals_pagination_info_accuracy(self):
        """Проверка точности paginationInfo"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes {
                    roleId
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
        result1 = assert_graphql_success(response1, "roleRightGoals")
        
        # Запрос с limit=10
        response2 = graphql_query(
            query,
            variables={"pagination": {"limit": 10, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "roleRightGoals")
        
        # totalCount должен быть одинаковым
        assert result1["paginationInfo"]["totalCount"] == result2["paginationInfo"]["totalCount"]
        
        # totalPages должен различаться
        assert result1["paginationInfo"]["totalPages"] >= result2["paginationInfo"]["totalPages"]

    def test_role_right_goals_query_offset_beyond_total(self):
        """Запрос с offset больше общего количества записей"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes {
                    roleId
                }
                pageInfo {
                    hasPreviousPage
                    hasNextPage
                }
                paginationInfo {
                    totalCount
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"pagination": {"limit": 10, "offset": 999999}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) == 0
        assert result["pageInfo"]["hasPreviousPage"] is True
        assert result["pageInfo"]["hasNextPage"] is False


class TestRoleRightGoalIntegrity:
    """Тесты для проверки целостности данных role_right_goal"""

    def test_all_rights_have_valid_references(self):
        """Проверка что все связи имеют валидные ссылки на role, right, goal"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes {
                    roleId
                    rightId
                    goalId
                    role { id }
                    right { id }
                    goal { id }
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"pagination": {"limit": 100, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        
        # Проверяем что все ссылки валидны
        for rrg in result["nodes"]:
            assert rrg["role"]["id"] == rrg["roleId"]
            assert rrg["right"]["id"] == rrg["rightId"]
            assert rrg["goal"]["id"] == rrg["goalId"]

    def test_admin_role_has_expected_rights(self):
        """Проверка что у admin роли есть ожидаемые права"""
        # Получаем ID admin роли
        roles_query = """
        query GetRoles($filter: RoleFilterInput) {
            roles(filter: $filter) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        roles_response = graphql_query(
            roles_query,
            variables={"filter": {"name": "admin"}},
            headers=ADMIN_HEADERS
        )
        
        roles_result = assert_graphql_success(roles_response, "roles")
        assert len(roles_result["nodes"]) > 0
        admin_id = roles_result["nodes"][0]["id"]
        
        # Получаем все права admin роли (увеличиваем лимит до 50)
        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput, $pagination: PaginationInput) {
            roleRightGoals(filter: $filter, pagination: $pagination) {
                nodes {
                    rightId
                    goalId
                    right { name }
                    goal { name }
                }
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={
                "filter": {"roleId": admin_id},
                "pagination": {"limit": 50, "offset": 0}  # ← Увеличиваем лимит
            },
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        
        # Проверяем наличие ключевых прав
        rights_set = {(rrg["rightId"], rrg["goalId"]) for rrg in result["nodes"]}
        
        # У admin должно быть право grant -> roles (5, 4)
        assert (5, 4) in rights_set, "У admin роли должно быть право grant -> roles"
        
        # Дополнительные проверки
        assert (1, 3) in rights_set, "view -> users"
        assert (3, 3) in rights_set, "edit -> users"
        assert (4, 3) in rights_set, "delete -> users"

    def test_no_duplicate_role_right_goal_combinations(self):
        """Проверка что нет дублирующихся комбинаций (role_id, right_id, goal_id)"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes {
                    roleId
                    rightId
                    goalId
                }
            }
        }
        """
        
        # Получаем все записи
        all_records = []
        offset = 0
        limit = 100
        
        while True:
            response = graphql_query(
                query,
                variables={"pagination": {"limit": limit, "offset": offset}},
                headers=ADMIN_HEADERS
            )
            
            result = assert_graphql_success(response, "roleRightGoals")
            all_records.extend(result["nodes"])
            
            if len(result["nodes"]) < limit:
                break
            
            offset += limit
        
        # Проверяем на дубликаты
        combinations = [(r["roleId"], r["rightId"], r["goalId"]) for r in all_records]
        unique_combinations = set(combinations)
        
        assert len(combinations) == len(unique_combinations), "Обнаружены дублирующиеся связи role_right_goal"
