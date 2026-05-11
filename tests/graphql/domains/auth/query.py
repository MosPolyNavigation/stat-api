"""Тесты для GraphQL Query операций с целями (Goal) в домене auth."""
import pytest
import uuid

from tests.base import client
from tests.graphql.base import (
    graphql_query, assert_graphql_success, assert_graphql_error, unique_login
)

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


# =============================================================================
# Тесты для Goal Query
# =============================================================================
class TestGoalQueries:
    """Тесты для GraphQL query операций с целями."""

    def test_goals_query_success(self):
        """Успешное получение списка целей с пагинацией."""
        query = """
        query GetGoals($pagination: PaginationInput, $filter: GoalFilterInput) {
            goals(pagination: $pagination, filter: $filter) {
                nodes { id name }
                pageInfo { hasPreviousPage hasNextPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response = graphql_query(
            query,
            variables={
                "pagination": {"page": 1, "pageSize": 10},
                "filter": None
            },
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goals")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) >= 8
        assert result["paginationInfo"]["totalCount"] >= 8

    def test_goals_query_with_filter_id(self):
        """Фильтрация целей по id."""
        query = """
        query GetGoals($filter: GoalFilterInput) {
            goals(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            # 🔹 Новый синтаксис фильтра: { id: { eq: 1 } } вместо { id: 1 }
            variables={"filter": {"id": {"eq": 1}}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goals")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == 1
        assert result["nodes"][0]["name"] == "stats"

    def test_goals_query_with_filter_name(self):
        """Фильтрация целей по name."""
        query = """
        query GetGoals($filter: GoalFilterInput) {
            goals(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"name": {"eq": "users"}}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goals")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "users"

    def test_goals_query_with_string_filter_contains(self):
        """Фильтрация целей по name с оператором contains."""
        query = """
        query GetGoals($filter: GoalFilterInput) {
            goals(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"name": {"contains": "ser"}}},  # найдёт "users"
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goals")
        assert len(result["nodes"]) >= 1
        assert all("ser" in n["name"].lower() for n in result["nodes"])

    def test_goals_query_pagination(self):
        """Проверка пагинации целей."""
        query = """
        query GetGoals($pagination: PaginationInput) {
            goals(pagination: $pagination) {
                nodes { id name }
                pageInfo { hasPreviousPage hasNextPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        # 🔹 Первая страница: page=1, pageSize=3
        response1 = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 3}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "goals")

        # 🔹 Вторая страница: page=2, pageSize=3
        response2 = graphql_query(
            query,
            variables={"pagination": {"page": 2, "pageSize": 3}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "goals")

        # Проверяем, что данные на страницах разные
        if result1["nodes"] and result2["nodes"]:
            ids1 = {n["id"] for n in result1["nodes"]}
            ids2 = {n["id"] for n in result2["nodes"]}
            assert ids1.isdisjoint(ids2), "Страницы не должны пересекаться"

        # Проверяем pageInfo
        assert result1["pageInfo"]["hasPreviousPage"] is False
        assert result1["paginationInfo"]["currentPage"] == 1
        assert result2["paginationInfo"]["currentPage"] == 2

    def test_goals_query_all_expected_goals_exist(self):
        """Проверка, что все ожидаемые цели существуют."""
        query = """
        query GetGoals {
            goals(pagination: {page: 1, pageSize: 20}) {
                nodes { id name }
            }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        result = assert_graphql_success(response, "goals")

        goals_map = {g["id"]: g["name"] for g in result["nodes"]}
        assert goals_map.get(1) == "stats"
        assert goals_map.get(3) == "users"
        assert goals_map.get(4) == "roles"
        assert goals_map.get(8) == "nav_data"

    def test_goals_query_with_user_pass_goal(self):
        """Проверка, что цель user_pass существует (ID: 9)."""
        query = """
        query GetGoals($filter: GoalFilterInput) {
            goals(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"id": {"eq": 9}}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goals")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "user_pass"

    def test_goals_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр целей."""
        test_login = f"noperms_{uuid.uuid4().hex[:8]}"

        # Создаём пользователя без прав
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login }
        }
        """
        graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )

        # Получаем токен пользователя
        token_resp = client.post(
            "/api/auth/token",
            data={"username": test_login, "password": "pass123"}
        )
        user_token = token_resp.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Пытаемся получить список целей
        query = """
        query GetGoals {
            goals(pagination: {page: 1, pageSize: 10}) { nodes { id name } }
        }
        """
        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")

    def test_goals_query_pagination_info_accuracy(self):
        """Проверка точности paginationInfo для целей."""
        query = """
        query GetGoals($pagination: PaginationInput) {
            goals(pagination: $pagination) {
                nodes { id }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        # Запрос с pageSize=1
        response1 = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 1}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "goals")

        # Запрос с pageSize=10
        response2 = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 10}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "goals")

        # totalCount должен быть одинаковым
        assert result1["paginationInfo"]["totalCount"] == result2["paginationInfo"]["totalCount"]
        # totalPages должен отличаться
        assert result1["paginationInfo"]["totalPages"] >= result2["paginationInfo"]["totalPages"]

    def test_goals_query_order_by_name_asc(self):
        """Проверка сортировки целей по имени (ASC)."""
        query = """
        query GetGoals($orderBy: GoalOrderByInput) {
            goals(orderBy: $orderBy, pagination: {page: 1, pageSize: 20}) {
                nodes { id name }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"orderBy": {"name": "ASC"}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goals")
        names = [n["name"] for n in result["nodes"]]
        assert names == sorted(names)

    def test_goals_query_order_by_id_desc(self):
        """Проверка сортировки целей по ID (DESC)."""
        query = """
        query GetGoals($orderBy: GoalOrderByInput) {
            goals(orderBy: $orderBy, pagination: {page: 1, pageSize: 20}) {
                nodes { id name }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"orderBy": {"id": "DESC"}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goals")
        ids = [n["id"] for n in result["nodes"]]
        assert ids == sorted(ids, reverse=True)

    def test_goal_single_by_id(self):
        """Получение одной цели по ID."""
        query = """
        query GetGoal($id: Int!) {
            goal(id: $id) { id name }
        }
        """
        response = graphql_query(
            query,
            variables={"id": 1},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "goal")
        assert result["id"] == 1
        assert result["name"] == "stats"

    def test_goal_single_not_found(self):
        """Запрос несуществующей цели."""
        query = """
        query GetGoal($id: Int!) {
            goal(id: $id) { id name }
        }
        """
        response = graphql_query(
            query,
            variables={"id": 999999},
            headers=ADMIN_HEADERS
        )
        assert response["status_code"] == 200
        assert response["data"]["data"]["goal"] is None


# =============================================================================
# Тесты для Role Query
# =============================================================================
class TestRoleQueries:
    """Тесты для GraphQL query операций с ролями."""

    def test_roles_query_success(self):
        """Успешное получение списка ролей с пагинацией."""
        query = """
        query GetRoles($pagination: PaginationInput, $filter: RoleFilterInput) {
            roles(pagination: $pagination, filter: $filter) {
                nodes { id name }
                pageInfo { hasPreviousPage hasNextPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response = graphql_query(
            query,
            variables={
                "pagination": {"page": 1, "pageSize": 10},
                "filter": None
            },
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "roles")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) >= 1  # Admin role должна существовать
        assert result["paginationInfo"]["totalCount"] >= 1

    def test_roles_query_with_filter_name(self):
        """Фильтрация ролей по name."""
        query = """
        query GetRoles($filter: RoleFilterInput) {
            roles(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            # 🔹 Новый синтаксис фильтра: { name: { eq: "admin" } }
            variables={"filter": {"name": {"eq": "admin"}}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "roles")
        assert len(result["nodes"]) >= 1
        assert all(n["name"] == "admin" for n in result["nodes"])

    def test_roles_query_with_filter_id(self):
        """Фильтрация ролей по id."""
        query = """
        query GetRoles($filter: RoleFilterInput) {
            roles(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"id": {"eq": 1}}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "roles")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == 1

    def test_roles_query_pagination(self):
        """Проверка пагинации ролей."""
        query = """
        query GetRoles($pagination: PaginationInput) {
            roles(pagination: $pagination) {
                nodes { id name }
                pageInfo { hasPreviousPage hasNextPage }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        # 🔹 Первая страница: page=1, pageSize=1
        response1 = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 1}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "roles")

        # 🔹 Вторая страница: page=2, pageSize=1
        response2 = graphql_query(
            query,
            variables={"pagination": {"page": 2, "pageSize": 1}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "roles")

        # Проверяем, что данные на страницах разные (если их больше 1)
        if result1["nodes"] and result2["nodes"]:
            ids1 = {n["id"] for n in result1["nodes"]}
            ids2 = {n["id"] for n in result2["nodes"]}
            assert ids1.isdisjoint(ids2), "Страницы не должны пересекаться"

        assert result1["pageInfo"]["hasPreviousPage"] is False
        assert result1["paginationInfo"]["currentPage"] == 1
        assert result2["paginationInfo"]["currentPage"] == 2

    def test_role_single_by_id(self):
        """Получение одной роли по ID."""
        query = """
        query GetRole($id: Int!) {
            role(id: $id) { id name }
        }
        """
        response = graphql_query(
            query,
            variables={"id": 1},  # 🔹 Аргумент 'id', не 'roleId'
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "role")
        assert result["id"] == 1
        assert result["name"] == "admin"

    def test_role_single_not_found(self):
        """Запрос несуществующей роли."""
        query = """
        query GetRole($id: Int!) {
            role(id: $id) { id name }
        }
        """
        response = graphql_query(
            query,
            variables={"id": 999999},
            headers=ADMIN_HEADERS
        )
        assert response["status_code"] == 200
        assert response["data"]["data"]["role"] is None

    def test_roles_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр ролей."""
        test_login = f"noperms_{uuid.uuid4().hex[:8]}"

        # Создаём пользователя без прав
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login }
        }
        """
        graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )

        # Получаем токен пользователя
        token_resp = client.post("/api/auth/token", data={"username": test_login, "password": "pass123"})
        user_token = token_resp.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Пытаемся получить список ролей
        query = """
        query GetRoles {
            roles(pagination: {page: 1, pageSize: 10}) { nodes { id name } }
        }
        """
        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")

    def test_roles_query_order_by_name_asc(self):
        """Проверка сортировки ролей по имени (ASC)."""
        query = """
        query GetRoles($orderBy: RoleOrderByInput) {
            roles(orderBy: $orderBy, pagination: {page: 1, pageSize: 20}) {
                nodes { id name }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"orderBy": {"name": "ASC"}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "roles")
        names = [n["name"] for n in result["nodes"]]
        assert names == sorted(names)

    def test_roles_query_order_by_id_desc(self):
        """Проверка сортировки ролей по ID (DESC)."""
        query = """
        query GetRoles($orderBy: RoleOrderByInput) {
            roles(orderBy: $orderBy, pagination: {page: 1, pageSize: 20}) {
                nodes { id name }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"orderBy": {"id": "DESC"}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "roles")
        ids = [n["id"] for n in result["nodes"]]
        assert ids == sorted(ids, reverse=True)


class TestRightQueries:
    """Тесты для GraphQL query операций с правами"""

    def test_rights_query_success(self):
        """Успешное получение списка прав с пагинацией"""
        query = """
        query GetRights($pagination: PaginationInput, $filter: RightFilterInput) {
            rights(pagination: $pagination, filter: $filter) {
                nodes { id name }
                pageInfo { hasPreviousPage hasNextPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 10}, "filter": None},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "rights")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) == 5
        assert result["paginationInfo"]["totalCount"] == 5

    def test_rights_query_with_filter_id(self):
        """Фильтрация прав по id"""
        query = """
        query GetRights($filter: RightFilterInput) {
            rights(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"id": {"eq": 1}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "rights")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == 1
        assert result["nodes"][0]["name"] == "view"

    def test_rights_query_with_filter_name(self):
        """Фильтрация прав по name"""
        query = """
        query GetRights($filter: RightFilterInput) {
            rights(filter: $filter) { nodes { id name } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"name": {"eq": "create"}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "rights")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["name"] == "create"

    def test_rights_query_pagination(self):
        """Проверка пагинации прав"""
        query = """
        query GetRights($pagination: PaginationInput) {
            rights(pagination: $pagination) {
                nodes { id name }
                pageInfo { hasPreviousPage hasNextPage }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response1 = graphql_query(
            query, variables={"pagination": {"page": 1, "pageSize": 2}}, headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "rights")

        response2 = graphql_query(
            query, variables={"pagination": {"page": 2, "pageSize": 2}}, headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "rights")

        assert result1["nodes"][0]["id"] != result2["nodes"][0]["id"]
        assert result1["pageInfo"]["hasPreviousPage"] is False
        assert result1["pageInfo"]["hasNextPage"] is True

    def test_rights_query_all_expected_rights_exist(self):
        """Проверка что все ожидаемые права существуют"""
        query = """
        query GetRights {
            rights(pagination: {page: 1, pageSize: 10}) { nodes { id name } }
        }
        """
        response = graphql_query(query, headers=ADMIN_HEADERS)
        result = assert_graphql_success(response, "rights")
        rights_map = {r["id"]: r["name"] for r in result["nodes"]}
        assert rights_map.get(1) == "view"
        assert rights_map.get(2) == "create"
        assert rights_map.get(3) == "edit"
        assert rights_map.get(4) == "delete"

    def test_rights_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр прав"""
        test_login = f"noperms_{uuid.uuid4().hex[:8]}"
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login }
        }
        """
        graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS,
        )

        token_response = client.post(
            "/api/auth/token", data={"username": test_login, "password": "pass123"}
        )
        user_token = token_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        query = """
        query GetRights {
            rights(pagination: {page: 1, pageSize: 10}) { nodes { id name } }
        }
        """
        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")


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
                    role { id name }
                    right { id name }
                    goal { id name }
                }
                pageInfo { hasPreviousPage hasNextPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response = graphql_query(
            query,
            variables={
                "pagination": {"page": 1, "pageSize": 10},
                "filter": None,
            },
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) > 0
        assert result["paginationInfo"]["totalCount"] >= 1

    def test_role_right_goals_query_with_filter_role_id(self):
        """Фильтрация связей по role_id"""
        roles_query = """
        query GetRoles {
            roles(pagination: {page: 1, pageSize: 1}) { nodes { id name } }
        }
        """
        roles_response = graphql_query(roles_query, headers=ADMIN_HEADERS)
        admin_id = roles_response["data"]["data"]["roles"]["nodes"][0]["id"]

        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) { nodes { roleId rightId goalId } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"roleId": {"eq": admin_id}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        assert all(rrg["roleId"] == admin_id for rrg in result["nodes"])

    def test_role_right_goals_query_with_filter_right_id(self):
        """Фильтрация связей по right_id"""
        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) { nodes { roleId rightId goalId } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"rightId": {"eq": 1}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        assert all(rrg["rightId"] == 1 for rrg in result["nodes"])

    def test_role_right_goals_query_with_filter_goal_id(self):
        """Фильтрация связей по goal_id"""
        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) { nodes { roleId rightId goalId } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"goalId": {"eq": 1}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
        assert all(rrg["goalId"] == 1 for rrg in result["nodes"])

    def test_role_right_goals_query_with_combined_filters(self):
        """Фильтрация связей по нескольким полям одновременно"""
        roles_query = """
        query GetRoles {
            roles(pagination: {page: 1, pageSize: 1}) { nodes { id } }
        }
        """
        roles_response = graphql_query(roles_query, headers=ADMIN_HEADERS)
        admin_id = roles_response["data"]["data"]["roles"]["nodes"][0]["id"]

        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput) {
            roleRightGoals(filter: $filter) { nodes { roleId rightId goalId } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"roleId": {"eq": admin_id}, "rightId": {"eq": 1}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        assert all(rrg["roleId"] == admin_id and rrg["rightId"] == 1 for rrg in result["nodes"])

    def test_role_right_goals_query_pagination(self):
        """Проверка пагинации связей"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes { roleId rightId goalId }
                pageInfo { hasPreviousPage hasNextPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response1 = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 5}},
            headers=ADMIN_HEADERS,
        )
        result1 = assert_graphql_success(response1, "roleRightGoals")

        response2 = graphql_query(
            query,
            variables={"pagination": {"page": 2, "pageSize": 5}},
            headers=ADMIN_HEADERS,
        )
        result2 = assert_graphql_success(response2, "roleRightGoals")

        assert "hasPreviousPage" in result1["pageInfo"]
        assert "hasNextPage" in result1["pageInfo"]
        assert result1["pageInfo"]["hasPreviousPage"] is False

        if len(result1["nodes"]) == 5 and len(result2["nodes"]) > 0:
            assert result1["nodes"][0] != result2["nodes"][0]

    def test_role_right_goal_query_success(self):
        """Успешное получение конкретной связи"""
        list_query = """
        query GetRoleRightGoals {
            roleRightGoals(pagination: {page: 1, pageSize: 1}) {
                nodes { roleId rightId goalId }
            }
        }
        """
        list_response = graphql_query(list_query, headers=ADMIN_HEADERS)
        first_rrg = list_response["data"]["data"]["roleRightGoals"]["nodes"][0]

        query = """
        query GetRoleRightGoal($roleId: Int!, $rightId: Int!, $goalId: Int!) {
            roleRightGoal(roleId: $roleId, rightId: $rightId, goalId: $goalId) {
                roleId
                rightId
                goalId
                role { id name }
                right { id name }
                goal { id name }
            }
        }
        """
        response = graphql_query(
            query,
            variables={
                "roleId": first_rrg["roleId"],
                "rightId": first_rrg["rightId"],
                "goalId": first_rrg["goalId"],
            },
            headers=ADMIN_HEADERS,
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
                roleId rightId goalId
            }
        }
        """
        response = graphql_query(
            query,
            variables={"roleId": 999, "rightId": 999, "goalId": 999},
            headers=ADMIN_HEADERS,
        )
        assert response["status_code"] == 200
        assert response["data"]["data"]["roleRightGoal"] is None

    def test_role_right_goals_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр ролей"""
        test_login = f"noperms_{uuid.uuid4().hex[:8]}"
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login }
        }
        """
        graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass1234", "isActive": True}},
            headers=ADMIN_HEADERS,
        )
        token_response = client.post("/api/auth/token", data={"username": test_login, "password": "pass1234"})
        user_token = token_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        query = """
        query GetRoleRightGoals {
            roleRightGoals(pagination: {page: 1, pageSize: 10}) { nodes { roleId rightId goalId } }
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
                    roleId rightId goalId
                    role { id name }
                    right { id name }
                    goal { id name }
                }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 5}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0
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
                nodes { roleId }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response1 = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 1}},
            headers=ADMIN_HEADERS,
        )
        result1 = assert_graphql_success(response1, "roleRightGoals")

        response2 = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 10}},
            headers=ADMIN_HEADERS,
        )
        result2 = assert_graphql_success(response2, "roleRightGoals")

        assert result1["paginationInfo"]["totalCount"] == result2["paginationInfo"]["totalCount"]
        assert result1["paginationInfo"]["totalPages"] >= result2["paginationInfo"]["totalPages"]

    def test_role_right_goals_query_page_beyond_total(self):
        """Запрос со страницей больше общего количества страниц"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes { roleId }
                pageInfo { hasPreviousPage hasNextPage }
                paginationInfo { totalCount }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"pagination": {"page": 999999, "pageSize": 10}},
            headers=ADMIN_HEADERS,
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
                    roleId rightId goalId
                    role { id }
                    right { id }
                    goal { id }
                }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 100}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        for rrg in result["nodes"]:
            assert rrg["role"]["id"] == rrg["roleId"]
            assert rrg["right"]["id"] == rrg["rightId"]
            assert rrg["goal"]["id"] == rrg["goalId"]

    def test_admin_role_has_expected_rights(self):
        """Проверка что у admin роли есть ожидаемые права"""
        roles_query = """
        query GetRoles($filter: RoleFilterInput) {
            roles(filter: $filter) { nodes { id name } }
        }
        """
        roles_response = graphql_query(
            roles_query,
            variables={"filter": {"name": {"eq": "admin"}}},
            headers=ADMIN_HEADERS,
        )
        roles_result = assert_graphql_success(roles_response, "roles")
        assert len(roles_result["nodes"]) > 0
        admin_id = roles_result["nodes"][0]["id"]

        query = """
        query GetRoleRightGoals($filter: RoleRightGoalFilterInput, $pagination: PaginationInput) {
            roleRightGoals(filter: $filter, pagination: $pagination) {
                nodes {
                    rightId goalId canGrant
                    right { name }
                    goal { name }
                }
            }
        }
        """
        response = graphql_query(
            query,
            variables={
                "filter": {"roleId": {"eq": admin_id}},
                "pagination": {"page": 1, "pageSize": 50},
            },
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "roleRightGoals")
        assert len(result["nodes"]) > 0

        rights_set = {(rrg["rightId"], rrg["goalId"]) for rrg in result["nodes"]}
        assert result["nodes"], "У admin роли должны быть права"
        assert all(rrg["canGrant"] is True for rrg in result["nodes"]), "Все права admin должны быть делегируемыми"
        assert (1, 3) in rights_set, "view -> users"
        assert (3, 3) in rights_set, "edit -> users"
        assert (4, 3) in rights_set, "delete -> users"

    def test_no_duplicate_role_right_goal_combinations(self):
        """Проверка что нет дублирующихся комбинаций (role_id, right_id, goal_id)"""
        query = """
        query GetRoleRightGoals($pagination: PaginationInput) {
            roleRightGoals(pagination: $pagination) {
                nodes { roleId rightId goalId }
            }
        }
        """
        all_records = []
        page = 1
        page_size = 100

        while True:
            response = graphql_query(
                query,
                variables={"pagination": {"page": page, "pageSize": page_size}},
                headers=ADMIN_HEADERS,
            )
            result = assert_graphql_success(response, "roleRightGoals")
            all_records.extend(result["nodes"])
            if len(result["nodes"]) < page_size:
                break
            page += 1

        combinations = [(r["roleId"], r["rightId"], r["goalId"]) for r in all_records]
        unique_combinations = set(combinations)
        assert len(combinations) == len(unique_combinations), "Обнаружены дублирующиеся связи role_right_goal"


class TestUserRoleQueries:
    """Тесты для GraphQL query операций с user_role"""

    def test_user_roles_query_success(self):
        """Успешное получение списка связей пользователь-роль с пагинацией"""
        query = """
        query GetUserRoles($pagination: PaginationInput, $filter: UserRoleFilterInput) {
            userRoles(pagination: $pagination, filter: $filter) {
                nodes {
                    userId
                    roleId
                    user {
                        id
                        login
                    }
                    role {
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
                "pagination": {"pageSize": 10, "page": 1},
                "filter": None
            },
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "userRoles")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)

    def test_user_roles_query_with_filter_user_id(self):
        """Фильтрация связей по user_id"""
        # Создаём пользователя
        test_login = f"filteruser_{uuid.uuid4().hex[:8]}"
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
        user_id = create_response["data"]["data"]["createUser"]["id"]

        # Назначаем роль
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data)
        }
        """
        graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )

        # Фильтруем по user_id
        query = """
        query GetUserRoles($filter: UserRoleFilterInput) {
            userRoles(filter: $filter) {
                nodes {
                    userId
                    roleId
                }
            }
        }
        """

        response = graphql_query(
            query,
            variables={"filter": {"userId": {"eq": user_id}}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "userRoles")
        assert len(result["nodes"]) > 0
        assert all(ur["userId"] == user_id for ur in result["nodes"])

    def test_user_roles_query_with_filter_role_id(self):
        """Фильтрация связей по role_id"""
        query = """
        query GetUserRoles($filter: UserRoleFilterInput) {
            userRoles(filter: $filter) {
                nodes {
                    userId
                    roleId
                }
            }
        }
        """

        response = graphql_query(
            query,
            variables={"filter": {"roleId": {"eq": 1}}},  # Admin role
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "userRoles")
        assert len(result["nodes"]) > 0
        assert all(ur["roleId"] == 1 for ur in result["nodes"])

    def test_user_roles_query_pagination(self):
        """Проверка пагинации связей пользователь-роль"""
        query = """
        query GetUserRoles($pagination: PaginationInput) {
            userRoles(pagination: $pagination) {
                nodes {
                    userId
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

        # Первая страница
        response1 = graphql_query(
            query,
            variables={"pagination": {"pageSize": 5, "page": 1}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "userRoles")

        # Проверяем pageInfo
        assert result1["pageInfo"]["hasPreviousPage"] is False

    def test_user_role_query_success(self):
        """Успешное получение конкретной связи пользователь-роль"""
        # Получаем первую связь
        list_query = """
        query GetUserRoles {
            userRoles(pagination: {pageSize: 1}) {
                nodes {
                    userId
                    roleId
                }
            }
        }
        """
        list_response = graphql_query(list_query, headers=ADMIN_HEADERS)

        if len(list_response["data"]["data"]["userRoles"]["nodes"]) > 0:
            first_ur = list_response["data"]["data"]["userRoles"]["nodes"][0]

            # Получаем конкретную связь
            query = """
            query GetUserRole($userId: Int!, $roleId: Int!) {
                userRole(userId: $userId, roleId: $roleId) {
                    userId
                    roleId
                    user {
                        id
                        login
                    }
                    role {
                        id
                        name
                    }
                }
            }
            """

            response = graphql_query(
                query,
                variables={"userId": first_ur["userId"], "roleId": first_ur["roleId"]},
                headers=ADMIN_HEADERS
            )

            result = assert_graphql_success(response, "userRole")
            assert result["userId"] == first_ur["userId"]
            assert result["roleId"] == first_ur["roleId"]

    def test_user_role_query_not_found(self):
        """Связь пользователь-роль не найдена"""
        query = """
        query GetUserRole($userId: Int!, $roleId: Int!) {
            userRole(userId: $userId, roleId: $roleId) {
                userId
                roleId
            }
        }
        """

        response = graphql_query(
            query,
            variables={"userId": 999999, "roleId": 999999},
            headers=ADMIN_HEADERS
        )

        # GraphQL возвращает null для не найденного объекта
        assert response["status_code"] == 200
        assert response["data"]["data"]["userRole"] is None

    def test_user_roles_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр ролей"""
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

        # Пытаемся получить список связей
        query = """
        query GetUserRoles {
            userRoles(pagination: {pageSize: 10}) {
                nodes {
                    userId
                    roleId
                }
            }
        }
        """

        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")


class TestUserQueries:
    """Тесты для GraphQL query операций с пользователями"""

    def test_users_query_success(self):
        """Успешное получение списка пользователей с пагинацией"""
        query = """
        query GetUsers($pagination: PaginationInput, $filter: UserFilterInput) {
            users(pagination: $pagination, filter: $filter) {
                nodes {
                    id
                    login
                    fio
                    isActive
                    registrationDate
                    updatedAt
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
                "pagination": {"pageSize": 10, "page": 1},
                "filter": None
            },
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "users")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) > 0  # Админ должен существовать
        assert result["paginationInfo"]["totalCount"] >= 1

    def test_users_query_with_filter_login(self):
        """Фильтрация пользователей по login"""
        # Создаём тестового пользователя
        test_login = unique_login("filtertest")
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )

        # Фильтруем по login
        query = """
        query GetUsers($filter: UserFilterInput) {
            users(filter: $filter) {
                nodes {
                    id
                    login
                }
            }
        }
        """

        response = graphql_query(
            query,
            variables={"filter": {"login": {"eq": test_login}}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "users")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["login"] == test_login

    def test_users_query_with_filter_is_active(self):
        """Фильтрация пользователей по is_active"""
        query = """
        query GetUsers($filter: UserFilterInput) {
            users(filter: $filter) {
                nodes {
                    id
                    login
                    isActive
                }
            }
        }
        """

        response = graphql_query(
            query,
            variables={"filter": {"isActive": {"eq": True}}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "users")
        assert all(user["isActive"] is True for user in result["nodes"])

    def test_users_query_pagination(self):
        """Проверка пагинации пользователей"""
        query = """
        query GetUsers($pagination: PaginationInput) {
            users(pagination: $pagination) {
                nodes {
                    id
                    login
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
            variables={"pagination": {"pageSize": 1, "page": 1}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "users")

        # Вторая страница
        response2 = graphql_query(
            query,
            variables={"pagination": {"pageSize": 1, "page": 2}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "users")

        # Проверяем что данные разные
        if len(result1["nodes"]) > 0 and len(result2["nodes"]) > 0:
            assert result1["nodes"][0]["id"] != result2["nodes"][0]["id"]

        # Проверяем pageInfo
        assert "hasPreviousPage" in result1["pageInfo"]
        assert "hasNextPage" in result1["pageInfo"]
        assert result1["pageInfo"]["hasPreviousPage"] is False  # Первая страница

    def test_user_query_success(self):
        """Успешное получение конкретного пользователя"""
        # Получаем ID админа
        users_query = """
        query GetUsers {
            users(pagination: {pageSize: 1}) {
                nodes {
                    id
                    login
                }
            }
        }
        """
        users_response = graphql_query(users_query, headers=ADMIN_HEADERS)
        admin_id = users_response["data"]["data"]["users"]["nodes"][0]["id"]

        # Получаем конкретного пользователя
        query = """
        query GetUser($userId: Int!) {
            user(id: $userId) {
                id
                login
                fio
                isActive
                registrationDate
                updatedAt
            }
        }
        """

        response = graphql_query(
            query,
            variables={"userId": admin_id},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "user")
        assert result["id"] == admin_id
        assert result["login"] == "admin"
        assert result["isActive"] is True

    def test_user_query_not_found(self):
        """Пользователь не найден"""
        query = """
        query GetUser($Id: Int!) {
            user(id: $Id) {
                id
                login
            }
        }
        """

        response = graphql_query(
            query,
            variables={"Id": 999999},
            headers=ADMIN_HEADERS
        )

        # GraphQL возвращает null для не найденного объекта
        assert response["status_code"] == 200
        assert response["data"]["data"]["user"] is None

    def test_users_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр пользователей"""
        # Создаём пользователя без прав
        test_login = unique_login("noperms")
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        graphql_query(
            create_query,
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

        # Пытаемся получить список пользователей
        query = """
        query GetUsers {
            users(pagination: {pageSize: 10}) {
                nodes {
                    id
                    login
                }
            }
        }
        """

        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")


class TestRefreshTokenQueries:
    """Тесты для GraphQL query операций с refresh токенами"""

    def test_refresh_tokens_query_success(self):
        """Успешное получение списка refresh токенов с пагинацией"""
        query = """
        query GetRefreshTokens($pagination: PaginationInput, $filter: RefreshTokenFilterInput) {
            refreshTokens(pagination: $pagination, filter: $filter) {
                nodes {
                    id
                    userId
                    jti
                    expDate
                    browser
                    userIp
                    revoked
                    createdAt
                }
                pageInfo { hasPreviousPage hasNextPage startCursor endCursor }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        response = graphql_query(
            query,
            variables={"pagination": {"page": 1, "pageSize": 10}, "filter": None},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "refreshTokens")
        assert "nodes" in result
        assert "pageInfo" in result
        assert "paginationInfo" in result
        assert isinstance(result["nodes"], list)
        assert result["paginationInfo"]["totalCount"] >= 0

    def test_refresh_tokens_query_with_filter_user_id(self):
        """Фильтрация токенов по userId"""
        # Создаём пользователя и логинимся, чтобы гарантированно сгенерировать токен
        test_login = f"rt_user_{uuid.uuid4().hex[:8]}"
        create_q = """
        mutation CreateUser($data: CreateUserInput!) { createUser(data: $data) { id } }
        """
        create_resp = graphql_query(
            create_q,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS,
        )
        user_id = create_resp["data"]["data"]["createUser"]["id"]

        # Генерируем refresh token через REST login
        client.post("/api/auth/token", data={"username": test_login, "password": "pass123", "scope": "long"})

        query = """
        query GetRefreshTokens($filter: RefreshTokenFilterInput) {
            refreshTokens(filter: $filter) { nodes { id userId jti revoked } }
        }
        """
        response = graphql_query(
            query,
            variables={"filter": {"userId": {"eq": user_id}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "refreshTokens")
        assert len(result["nodes"]) > 0
        assert all(rt["userId"] == user_id for rt in result["nodes"])

    def test_refresh_tokens_query_with_filter_revoked(self):
        """Фильтрация токенов по статусу отзыва"""
        query = """
        query GetRefreshTokens($filter: RefreshTokenFilterInput) {
            refreshTokens(filter: $filter) { nodes { id revoked } }
        }
        """
        # Активные токены
        response = graphql_query(
            query,
            variables={"filter": {"revoked": {"eq": False}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(response, "refreshTokens")
        assert all(rt["revoked"] is False for rt in result["nodes"])

    def test_refresh_tokens_query_pagination(self):
        """Проверка пагинации refresh токенов"""
        query = """
        query GetRefreshTokens($pagination: PaginationInput) {
            refreshTokens(pagination: $pagination) {
                nodes { id jti }
                pageInfo { hasPreviousPage hasNextPage }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        resp1 = graphql_query(
            query, variables={"pagination": {"page": 1, "pageSize": 5}}, headers=ADMIN_HEADERS
        )
        res1 = assert_graphql_success(resp1, "refreshTokens")

        resp2 = graphql_query(
            query, variables={"pagination": {"page": 2, "pageSize": 5}}, headers=ADMIN_HEADERS
        )
        res2 = assert_graphql_success(resp2, "refreshTokens")

        assert res1["pageInfo"]["hasPreviousPage"] is False
        if res1["nodes"] and res2["nodes"]:
            ids1 = {n["id"] for n in res1["nodes"]}
            ids2 = {n["id"] for n in res2["nodes"]}
            assert ids1.isdisjoint(ids2), "Страницы не должны пересекаться"

    def test_refresh_token_single_by_id(self):
        """Получение одного refresh токена по ID"""
        list_q = """
        query GetRefreshTokens {
            refreshTokens(pagination: {page: 1, pageSize: 1}) { nodes { id userId } }
        }
        """
        list_resp = graphql_query(list_q, headers=ADMIN_HEADERS)
        nodes = list_resp["data"]["data"]["refreshTokens"]["nodes"]
        if not nodes:
            pytest.skip("No refresh tokens found in DB")

        token_id = nodes[0]["id"]
        query = """
        query GetRefreshToken($id: Int!) {
            refreshToken(id: $id) { id userId jti expDate revoked createdAt }
        }
        """
        resp = graphql_query(
            query, variables={"id": token_id}, headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(resp, "refreshToken")
        assert result["id"] == token_id

    def test_refresh_token_single_not_found(self):
        """Запрос несуществующего refresh токена"""
        query = """
        query GetRefreshToken($id: Int!) {
            refreshToken(id: $id) { id }
        }
        """
        resp = graphql_query(
            query, variables={"id": 999999}, headers=ADMIN_HEADERS
        )
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["refreshToken"] is None

    def test_refresh_tokens_query_no_permission(self):
        """Ошибка при отсутствии прав на просмотр refresh токенов"""
        test_login = f"noperms_rt_{uuid.uuid4().hex[:8]}"
        create_q = """
        mutation CreateUser($data: CreateUserInput!) { createUser(data: $data) { id login } }
        """
        graphql_query(
            create_q,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS,
        )
        token_resp = client.post("/api/auth/token", data={"username": test_login, "password": "pass123"})
        user_headers = {"Authorization": f"Bearer {token_resp.json()['access_token']}"}

        query = """
        query GetRefreshTokens {
            refreshTokens(pagination: {page: 1, pageSize: 10}) { nodes { id } }
        }
        """
        resp = graphql_query(query, headers=user_headers)
        assert_graphql_error(resp, "недостаточно прав")

    def test_refresh_tokens_query_with_nested_user(self):
        """Проверка разрешения вложенного поля user"""
        query = """
        query GetRefreshTokens($pagination: PaginationInput) {
            refreshTokens(pagination: $pagination) {
                nodes {
                    id
                    userId
                    user { id login }
                }
            }
        }
        """
        resp = graphql_query(
            query, variables={"pagination": {"page": 1, "pageSize": 5}}, headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(resp, "refreshTokens")
        assert len(result["nodes"]) > 0
        for rt in result["nodes"]:
            assert rt["user"] is not None
            assert "login" in rt["user"]
            assert rt["user"]["id"] == rt["userId"]

    def test_refresh_tokens_query_order_by_created_at_desc(self):
        """Проверка сортировки токенов по дате создания (DESC)"""
        query = """
        query GetRefreshTokens($orderBy: RefreshTokenOrderByInput, $pagination: PaginationInput) {
            refreshTokens(orderBy: $orderBy, pagination: $pagination) {
                nodes { id createdAt }
            }
        }
        """
        resp = graphql_query(
            query,
            variables={"orderBy": {"createdAt": "DESC"}, "pagination": {"page": 1, "pageSize": 20}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(resp, "refreshTokens")
        dates = [rt["createdAt"] for rt in result["nodes"]]
        assert dates == sorted(dates, reverse=True)

    def test_refresh_tokens_query_filter_by_jti(self):
        """Фильтрация токенов по jti (строковый фильтр)"""
        # Получаем первый токен, чтобы взять его jti
        list_q = """
        query GetRefreshTokens {
            refreshTokens(pagination: {page: 1, pageSize: 1}) { nodes { jti } }
        }
        """
        list_resp = graphql_query(list_q, headers=ADMIN_HEADERS)
        nodes = list_resp["data"]["data"]["refreshTokens"]["nodes"]
        if not nodes:
            pytest.skip("No refresh tokens to filter by jti")

        target_jti = nodes[0]["jti"]
        query = """
        query GetRefreshTokens($filter: RefreshTokenFilterInput) {
            refreshTokens(filter: $filter) { nodes { id jti } }
        }
        """
        resp = graphql_query(
            query,
            variables={"filter": {"jti": {"eq": target_jti}}},
            headers=ADMIN_HEADERS,
        )
        result = assert_graphql_success(resp, "refreshTokens")
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["jti"] == target_jti
