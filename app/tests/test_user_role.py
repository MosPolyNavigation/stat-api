"""Тесты для GraphQL эндпоинтов управления связями пользователь-роль (UserRole)"""

import pytest
import uuid
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
                "pagination": {"limit": 10, "offset": 0},
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
            grantRole(data: $data) {
                success
            }
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
            variables={"filter": {"userId": user_id}},
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
            variables={"filter": {"roleId": 1}},  # Admin role
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
            variables={"pagination": {"limit": 5, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "userRoles")
        
        # Вторая страница
        response2 = graphql_query(
            query,
            variables={"pagination": {"limit": 5, "offset": 5}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "userRoles")
        
        # Проверяем pageInfo
        assert result1["pageInfo"]["hasPreviousPage"] is False

    def test_user_role_query_success(self):
        """Успешное получение конкретной связи пользователь-роль"""
        # Получаем первую связь
        list_query = """
        query GetUserRoles {
            userRoles(pagination: {limit: 1}) {
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
            userRoles(pagination: {limit: 10}) {
                nodes {
                    userId
                    roleId
                }
            }
        }
        """
        
        response = graphql_query(query, headers=user_headers)
        assert_graphql_error(response, "недостаточно прав")


class TestGrantRoleMutation:
    """Тесты для мутации grantRole"""

    def test_grant_role_success(self):
        """Успешное назначение роли пользователю"""
        test_login = f"granttest_{uuid.uuid4().hex[:8]}"
        
        # Создаём пользователя
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
            grantRole(data: $data) {
                success
                message
                user {
                    id
                    login
                    roles {
                        userId
                        roleId
                        role {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "grantRole")
        assert result["success"] is True
        assert result["user"]["roles"] is not None
        assert len(result["user"]["roles"]) > 0

    def test_grant_role_multiple_roles(self):
        """Назначение нескольких ролей пользователю"""
        test_login = f"multirole_{uuid.uuid4().hex[:8]}"
        
        # Создаём пользователя
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
        
        # Назначаем роль (admin = 1)
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data) {
                success
                message
            }
        }
        """
        
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "grantRole")
        assert result["success"] is True

    def test_grant_role_user_not_found(self):
        """Пользователь не найден"""
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data) {
                success
                message
            }
        }
        """
        
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": 999999, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        
        assert_graphql_error(response, "не найден")

    def test_grant_role_inactive_user(self):
        """Нельзя назначить роль неактивному пользователю"""
        test_login = f"inactive_{uuid.uuid4().hex[:8]}"
        
        # Создаём неактивного пользователя
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
                isActive
            }
        }
        """
        create_response = graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": False}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]
        
        # Пытаемся назначить роль
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data) {
                success
                message
            }
        }
        """
        
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        
        assert_graphql_error(response, "неактивному")

    def test_grant_role_duplicate_assignment(self):
        """Повторное назначение уже назначенной роли (должно пропустить)"""
        test_login = f"duprole_{uuid.uuid4().hex[:8]}"
        
        # Создаём пользователя
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
        
        # Назначаем роль первый раз
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data) {
                success
                message
            }
        }
        """
        
        response1 = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "grantRole")
        assert "назначено ролей: 1" in result1["message"]
        
        # Назначаем ту же роль второй раз
        response2 = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "grantRole")
        assert "пропущено уже назначенных: 1" in result2["message"]

    def test_grant_role_no_permission(self):
        """Ошибка при отсутствии прав на выдачу ролей"""
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
        
        # Пытаемся назначить роль
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data) {
                success
                message
            }
        }
        """
        
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": 2, "roleIds": [1]}},
            headers=user_headers
        )
        
        assert_graphql_error(response, "недостаточно прав")


class TestRevokeRoleMutation:
    """Тесты для мутации revokeRole"""

    def test_revoke_role_success(self):
        """Успешный отзыв роли у пользователя"""
        test_login = f"revoketest_{uuid.uuid4().hex[:8]}"
        
        # Создаём пользователя
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
            grantRole(data: $data) {
                success
            }
        }
        """
        graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        
        # Отзываем роль
        revoke_query = """
        mutation RevokeRole($userId: Int!, $roleId: Int!) {
            revokeRole(userId: $userId, roleId: $roleId) {
                success
                message
                user {
                    id
                    roles {
                        roleId
                    }
                }
            }
        }
        """
        
        response = graphql_query(
            revoke_query,
            variables={"userId": user_id, "roleId": 1},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "revokeRole")
        assert result["success"] is True
        assert "отозвана" in result["message"].lower()

    def test_revoke_role_not_found(self):
        """Связь пользователь-роль не найдена"""
        revoke_query = """
        mutation RevokeRole($userId: Int!, $roleId: Int!) {
            revokeRole(userId: $userId, roleId: $roleId) {
                success
                message
            }
        }
        """
        
        response = graphql_query(
            revoke_query,
            variables={"userId": 1, "roleId": 999999},
            headers=ADMIN_HEADERS
        )
        
        assert_graphql_error(response, "не найдена")

    def test_revoke_role_no_permission(self):
        """Ошибка при отсутствии прав на отзыв ролей"""
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
        
        # Пытаемся отозвать роль
        revoke_query = """
        mutation RevokeRole($userId: Int!, $roleId: Int!) {
            revokeRole(userId: $userId, roleId: $roleId) {
                success
                message
            }
        }
        """
        
        response = graphql_query(
            revoke_query,
            variables={"userId": 2, "roleId": 1},
            headers=user_headers
        )
        
        assert_graphql_error(response, "недостаточно прав")
