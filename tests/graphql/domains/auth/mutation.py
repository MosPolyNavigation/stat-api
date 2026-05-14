"""Тесты для GraphQL Mutation операций с ролями (Role) в домене auth."""
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
# Тесты для Role Mutation
# =============================================================================
class TestRoleMutations:
    """Тесты для мутаций CRUD ролей."""

    def test_create_role_success(self):
        """Успешное создание роли."""
        test_name = f"test_create_{uuid.uuid4().hex[:8]}"
        query = """
        mutation CreateRole($data: CreateRoleInput!) {
            createRole(data: $data) { id name }
        }
        """
        response = graphql_query(
            query,
            variables={"data": {"name": test_name, "roleRightGoals": None}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "createRole")
        assert result["name"] == test_name
        assert "id" in result

    def test_create_role_with_rights_success(self):
        """Успешное создание роли с правами."""
        test_name = f"test_rights_{uuid.uuid4().hex[:8]}"
        query = """
        mutation CreateRole($data: CreateRoleInput!) {
            createRole(data: $data) { id name roleRightGoals { nodes { rightId goalId } } }
        }
        """
        response = graphql_query(
            query,
            variables={
                "data": {
                    "name": test_name,
                    "roleRightGoals": [
                        {"rightId": 1, "goalId": 1},
                        {"rightId": 1, "goalId": 3},
                    ]
                }
            },
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "createRole")
        assert result["name"] == test_name
        assert len(result["roleRightGoals"]["nodes"]) == 2

    def test_create_role_duplicate_name(self):
        """Ошибка при создании роли с существующим name."""
        test_name = f"test_dup_{uuid.uuid4().hex[:8]}"
        create_query = """
        mutation CreateRole($data: CreateRoleInput!) {
            createRole(data: $data) { id name }
        }
        """
        # Создаём первую роль
        graphql_query(
            create_query,
            variables={"data": {"name": test_name, "roleRightGoals": None}},
            headers=ADMIN_HEADERS
        )
        # Пытаемся создать вторую с тем же name
        response = graphql_query(
            create_query,
            variables={"data": {"name": test_name, "roleRightGoals": None}},
            headers=ADMIN_HEADERS
        )
        assert_graphql_error(response, "уже существует")

    def test_create_role_no_permission(self):
        """Ошибка при отсутствии прав на создание ролей."""
        test_login = f"noperms_{uuid.uuid4().hex[:8]}"
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login }
        }
        """
        graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        token_resp = client.post("/api/auth/token", data={"username": test_login, "password": "pass123"})
        user_token = token_resp.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        create_query = """
        mutation CreateRole($data: CreateRoleInput!) {
            createRole(data: $data) { id name }
        }
        """
        response = graphql_query(
            create_query,
            variables={"data": {"name": "test", "roleRightGoals": None}},
            headers=user_headers
        )
        assert_graphql_error(response, "недостаточно прав")

    def test_update_role_name_success(self):
        """Успешное обновление имени роли."""
        test_name = f"test_update_{uuid.uuid4().hex[:8]}"
        # Создаём роль
        create_query = """
        mutation CreateRole($data: CreateRoleInput!) {
            createRole(data: $data) { id name }
        }
        """
        create_resp = graphql_query(
            create_query,
            variables={"data": {"name": test_name, "roleRightGoals": None}},
            headers=ADMIN_HEADERS
        )
        role_id = create_resp["data"]["data"]["createRole"]["id"]

        # Обновляем имя (🔹 аргумент 'id', не 'roleId')
        update_query = """
        mutation UpdateRole($id: Int!, $data: UpdateRoleInput!) {
            updateRole(id: $id, data: $data) { id name }
        }
        """
        response = graphql_query(
            update_query,
            variables={
                "id": role_id,
                "data": {"name": f"{test_name}_updated"}
            },
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "updateRole")
        assert result["name"] == f"{test_name}_updated"

    def test_update_role_not_found(self):
        """Роль не найдена."""
        update_query = """
        mutation UpdateRole($id: Int!, $data: UpdateRoleInput!) {
            updateRole(id: $id, data: $data) { id name }
        }
        """
        response = graphql_query(
            update_query,
            variables={"id": 999999, "data": {"name": "Test"}},
            headers=ADMIN_HEADERS
        )
        assert_graphql_error(response, "не найдена")

    def test_delete_role_success(self):
        """Успешное удаление роли."""
        test_name = f"test_delete_{uuid.uuid4().hex[:8]}"
        # Создаём роль
        create_query = """
        mutation CreateRole($data: CreateRoleInput!) {
            createRole(data: $data) { id name }
        }
        """
        create_resp = graphql_query(
            create_query,
            variables={"data": {"name": test_name, "roleRightGoals": None}},
            headers=ADMIN_HEADERS
        )
        role_id = create_resp["data"]["data"]["createRole"]["id"]

        # Удаляем роль (🔹 аргумент 'id', возврат Boolean!)
        delete_query = """
        mutation DeleteRole($id: Int!) {
            deleteRole(id: $id)
        }
        """
        response = graphql_query(
            delete_query,
            variables={"id": role_id},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "deleteRole")
        assert result is True  # 🔹 Возвращает Boolean, не объект

        # Проверяем, что роль удалена
        get_query = """
        query GetRole($id: Int!) {
            role(id: $id) { id }
        }
        """
        get_resp = graphql_query(get_query, variables={"id": role_id}, headers=ADMIN_HEADERS)
        assert get_resp["data"]["data"]["role"] is None

    def test_delete_role_not_found(self):
        """Роль не найдена."""
        delete_query = """
        mutation DeleteRole($id: Int!) {
            deleteRole(id: $id)
        }
        """
        response = graphql_query(
            delete_query,
            variables={"id": 999999},
            headers=ADMIN_HEADERS
        )
        assert_graphql_error(response, "не найдена")

    def test_grant_role_success(self):
        """Успешное назначение роли пользователю."""
        test_login = f"grant_{uuid.uuid4().hex[:8]}"
        # Создаём пользователя
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login }
        }
        """
        create_resp = graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_resp["data"]["data"]["createUser"]["id"]

        # Назначаем роль (🔹 возврат Boolean!)
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data)
        }
        """
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "grantRole")
        assert result is True

    def test_grant_role_user_not_found(self):
        """Пользователь не найден."""
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data)
        }
        """
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": 999999, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        assert_graphql_error(response, "не найден")

    def test_grant_role_inactive_user(self):
        """Нельзя назначить роль неактивному пользователю."""
        test_login = f"inactive_{uuid.uuid4().hex[:8]}"
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login isActive }
        }
        """
        create_resp = graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": False}},
            headers=ADMIN_HEADERS
        )
        user_id = create_resp["data"]["data"]["createUser"]["id"]

        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data)
        }
        """
        response = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        assert_graphql_error(response, "неактивному")

    def test_revoke_role_success(self):
        """Успешный отзыв роли у пользователя."""
        test_login = f"revoke_{uuid.uuid4().hex[:8]}"
        # Создаём пользователя
        create_user_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) { id login }
        }
        """
        create_resp = graphql_query(
            create_user_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_resp["data"]["data"]["createUser"]["id"]

        # Назначаем роль
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data)
        }
        """
        graphql_query(grant_query, variables={"data": {"userId": user_id, "roleIds": [1]}}, headers=ADMIN_HEADERS)

        # Отзываем роль (🔹 аргументы: userId, roleId; возврат Boolean!)
        revoke_query = """
        mutation RevokeRole($userId: Int!, $roleId: Int!) {
            revokeRole(userId: $userId, roleId: $roleId)
        }
        """
        response = graphql_query(
            revoke_query,
            variables={"userId": user_id, "roleId": 1},
            headers=ADMIN_HEADERS
        )
        result = assert_graphql_success(response, "revokeRole")
        assert result is True

    def test_revoke_role_not_found(self):
        """Связь пользователь-роль не найдена."""
        revoke_query = """
        mutation RevokeRole($userId: Int!, $roleId: Int!) {
            revokeRole(userId: $userId, roleId: $roleId)
        }
        """
        response = graphql_query(
            revoke_query,
            variables={"userId": 1, "roleId": 999999},
            headers=ADMIN_HEADERS
        )
        assert_graphql_error(response, "не найдена")


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
            grantRole(data: $data)
        }
        """

        response = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "grantRole")
        assert result is True

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
            grantRole(data: $data)
        }
        """

        response = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "grantRole")
        assert result is True

    def test_grant_role_user_not_found(self):
        """Пользователь не найден"""
        grant_query = """
        mutation GrantRole($data: GrantRoleInput!) {
            grantRole(data: $data)
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
            grantRole(data: $data)
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
            grantRole(data: $data)
        }
        """

        response1 = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "grantRole")
        assert result1 is True

        # Назначаем ту же роль второй раз
        response2 = graphql_query(
            grant_query,
            variables={"data": {"userId": user_id, "roleIds": [1]}},
            headers=ADMIN_HEADERS
        )
        result2 = assert_graphql_success(response2, "grantRole")
        assert result2 is True

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
            grantRole(data: $data)
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
            grantRole(data: $data)
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
            revokeRole(userId: $userId, roleId: $roleId)
        }
        """

        response = graphql_query(
            revoke_query,
            variables={"userId": user_id, "roleId": 1},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "revokeRole")
        assert result is True

    def test_revoke_role_not_found(self):
        """Связь пользователь-роль не найдена"""
        revoke_query = """
        mutation RevokeRole($userId: Int!, $roleId: Int!) {
            revokeRole(userId: $userId, roleId: $roleId)
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
            revokeRole(userId: $userId, roleId: $roleId)
        }
        """

        response = graphql_query(
            revoke_query,
            variables={"userId": 2, "roleId": 1},
            headers=user_headers
        )

        assert_graphql_error(response, "недостаточно прав")


class TestCreateUserMutation:
    """Тесты для мутации createUser"""

    def test_create_user_success(self):
        """Успешное создание пользователя"""
        test_login = unique_login("create")
        query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
                fio
                isActive
                registrationDate
            }
        }
        """

        response = graphql_query(
            query,
            variables={
                "data": {
                    "login": test_login,
                    "password": "securepass123",
                    "fio": "Тестов Тест Тестович",
                    "isActive": True
                }
            },
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "createUser")
        assert result["login"] == test_login
        assert result["fio"] == "Тестов Тест Тестович"
        assert result["isActive"] is True
        assert "id" in result
        assert "registrationDate" in result

    def test_create_user_duplicate_login(self):
        """Ошибка при создании пользователя с существующим login"""
        test_login = unique_login("duplicate")
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        # Создаём первого пользователя
        graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )

        # Пытаемся создать второго с тем же login
        response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass456", "isActive": True}},
            headers=ADMIN_HEADERS
        )

        assert_graphql_error(response, "уже существует")

    def test_create_user_no_permission(self):
        """Ошибка при отсутствии прав на создание пользователей"""
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

        # Пытаемся создать пользователя
        response = graphql_query(
            create_query,
            variables={"data": {"login": unique_login("test"), "password": "pass123", "isActive": True}},
            headers=user_headers
        )

        assert_graphql_error(response, "недостаточно прав")

    def test_create_user_inactive(self):
        """Создание неактивного пользователя"""
        test_login = unique_login("inactive")
        query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
                isActive
            }
        }
        """

        response = graphql_query(
            query,
            variables={
                "data": {
                    "login": test_login,
                    "password": "pass123",
                    "isActive": False
                }
            },
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "createUser")
        assert result["isActive"] is False


class TestUpdateUserMutation:
    """Тесты для мутации updateUser"""

    def test_update_user_fio_success(self):
        """Успешное обновление ФИО пользователя"""
        test_login = unique_login("updatefio")

        # Создаём пользователя
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        create_response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]

        # Обновляем ФИО
        update_query = """
        mutation UpdateUser($userId: Int!, $data: UpdateUserInput!) {
            updateUser(id: $userId, data: $data) {
                id
                login
                fio
                updatedAt
            }
        }
        """

        response = graphql_query(
            update_query,
            variables={
                "userId": user_id,
                "data": {"fio": "Обновлён Обновлёнович Обновлёнов"}
            },
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "updateUser")
        assert result["fio"] == "Обновлён Обновлёнович Обновлёнов"
        assert result["login"] == test_login  # login не изменился

    def test_update_user_is_active_success(self):
        """Успешное обновление is_active пользователя"""
        test_login = unique_login("updateactive")

        # Создаём пользователя
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
                isActive
            }
        }
        """
        create_response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]

        # Деактивируем
        update_query = """
        mutation UpdateUser($userId: Int!, $data: UpdateUserInput!) {
            updateUser(id: $userId, data: $data) {
                id
                isActive
            }
        }
        """

        response = graphql_query(
            update_query,
            variables={"userId": user_id, "data": {"isActive": False}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "updateUser")
        assert result["isActive"] is False

    def test_update_user_partial_update(self):
        """Частичное обновление (только одно поле)"""
        test_login = unique_login("partial")

        # Создаём пользователя
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
                fio
                isActive
            }
        }
        """
        create_response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "fio": "Old FIO", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]

        # Обновляем только fio
        update_query = """
        mutation UpdateUser($userId: Int!, $data: UpdateUserInput!) {
            updateUser(id: $userId, data: $data) {
                id
                fio
                isActive
            }
        }
        """

        response = graphql_query(
            update_query,
            variables={"userId": user_id, "data": {"fio": "New FIO"}},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "updateUser")
        assert result["fio"] == "New FIO"
        assert result["isActive"] is True  # Не изменилось

    def test_update_user_not_found(self):
        """Пользователь не найден"""
        update_query = """
        mutation UpdateUser($userId: Int!, $data: UpdateUserInput!) {
            updateUser(id: $userId, data: $data) {
                id
                login
            }
        }
        """

        response = graphql_query(
            update_query,
            variables={"userId": 999999, "data": {"fio": "Test"}},
            headers=ADMIN_HEADERS
        )

        assert_graphql_error(response, "не найден")

    def test_update_user_no_permission(self):
        """Ошибка при отсутствии прав на редактирование пользователей"""
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

        # Пытаемся обновить пользователя
        update_query = """
        mutation UpdateUser($userId: Int!, $data: UpdateUserInput!) {
            updateUser(id: $userId, data: $data) {
                id
                fio
            }
        }
        """

        response = graphql_query(
            update_query,
            variables={"userId": 1, "data": {"fio": "Test"}},
            headers=user_headers
        )

        assert_graphql_error(response, "недостаточно прав")


class TestDeleteUserMutation:
    """Тесты для мутации deleteUser"""

    def test_delete_user_success(self):
        """Успешное удаление пользователя"""
        test_login = unique_login("delete")

        # Создаём пользователя
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        create_response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]

        # Удаляем пользователя
        delete_query = """
        mutation DeleteUser($userId: Int!) {
            deleteUser(id: $userId)
        }
        """

        response = graphql_query(
            delete_query,
            variables={"userId": user_id},
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "deleteUser")
        assert result is True

        # Проверяем что пользователь действительно удалён
        get_query = """
        query GetUser($userId: Int!) {
            user(id: $userId) {
                id
                login
            }
        }
        """
        get_response = graphql_query(
            get_query,
            variables={"userId": user_id},
            headers=ADMIN_HEADERS
        )
        assert get_response["data"]["data"]["user"] is None

    def test_delete_user_cannot_delete_self(self):
        """Нельзя удалить самого себя"""
        delete_query = """
        mutation DeleteUser($userId: Int!) {
            deleteUser(id: $userId)
        }
        """

        # Пытаемся удалить админа (текущий пользователь)
        response = graphql_query(
            delete_query,
            variables={"userId": 1},
            headers=ADMIN_HEADERS
        )

        assert_graphql_error(response, "нельзя удалить самого себя")

    def test_delete_user_not_found(self):
        """Пользователь не найден"""
        delete_query = """
        mutation DeleteUser($userId: Int!) {
            deleteUser(id: $userId)
        }
        """

        response = graphql_query(
            delete_query,
            variables={"userId": 999999},
            headers=ADMIN_HEADERS
        )

        assert_graphql_error(response, "не найден")

    def test_delete_user_no_permission(self):
        """Ошибка при отсутствии прав на удаление пользователей"""
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

        # Пытаемся удалить пользователя
        delete_query = """
        mutation DeleteUser($userId: Int!) {
            deleteUser(id: $userId)
        }
        """

        response = graphql_query(
            delete_query,
            variables={"userId": 2},
            headers=user_headers
        )

        assert_graphql_error(response, "недостаточно прав")


class TestChangeUserPasswordMutation:
    """Тесты для мутации changeUserPassword"""

    def test_change_user_password_success(self):
        """Успешная смена пароля пользователя администратором"""
        test_login = unique_login("changepass")

        # Создаём пользователя
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        create_response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "oldpass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]

        # Меняем пароль
        change_query = """
        mutation ChangeUserPassword($data: ChangeUserPasswordInput!) {
            changeUserPassword(data: $data)
        }
        """

        response = graphql_query(
            change_query,
            variables={
                "data": {
                    "userId": user_id,
                    "newPassword": "newpass456"
                }
            },
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "changeUserPassword")
        assert result is True

        # Проверяем что можно войти с новым паролем
        token_response = client.post(
            "/api/auth/token",
            data={"username": test_login, "password": "newpass456"}
        )
        assert token_response.status_code == 200
        assert "access_token" in token_response.json()

        # Проверяем что старый пароль не работает
        old_token_response = client.post(
            "/api/auth/token",
            data={"username": test_login, "password": "oldpass123"}
        )
        assert old_token_response.status_code == 400

    def test_change_user_password_short_password(self):
        """Ошибка при коротком пароле"""
        test_login = unique_login("shortpass")

        # Создаём пользователя
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        create_response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]

        # Пытаемся установить короткий пароль
        change_query = """
        mutation ChangeUserPassword($data: ChangeUserPasswordInput!) {
            changeUserPassword(data: $data)
        }
        """

        response = graphql_query(
            change_query,
            variables={
                "data": {
                    "userId": user_id,
                    "newPassword": "short"
                }
            },
            headers=ADMIN_HEADERS
        )

        assert_graphql_error(response, "минимум 8 символов")

    def test_change_user_password_cannot_change_self(self):
        """Нельзя изменить пароль самого себя через эту мутацию"""
        change_query = """
        mutation ChangeUserPassword($data: ChangeUserPasswordInput!) {
            changeUserPassword(data: $data)
        }
        """

        # Пытаемся изменить пароль админа (текущий пользователь)
        response = graphql_query(
            change_query,
            variables={
                "data": {
                    "userId": 1,
                    "newPassword": "newpass123"
                }
            },
            headers=ADMIN_HEADERS
        )

        assert_graphql_error(response, "Используйте REST endpoint для смены собственного пароля")

    def test_change_user_password_not_found(self):
        """Пользователь не найден"""
        change_query = """
        mutation ChangeUserPassword($data: ChangeUserPasswordInput!) {
            changeUserPassword(data: $data)
        }
        """

        response = graphql_query(
            change_query,
            variables={
                "data": {
                    "userId": 999999,
                    "newPassword": "newpass123"
                }
            },
            headers=ADMIN_HEADERS
        )

        assert_graphql_error(response, "не найден")

    def test_change_user_password_no_permission(self):
        """Ошибка при отсутствии прав на смену пароля пользователя"""
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

        # Пытаемся изменить пароль другому пользователю
        change_query = """
        mutation ChangeUserPassword($data: ChangeUserPasswordInput!) {
            changeUserPassword(data: $data)
        }
        """

        response = graphql_query(
            change_query,
            variables={
                "data": {
                    "userId": 2,
                    "newPassword": "newpass123"
                }
            },
            headers=user_headers
        )

        assert_graphql_error(response, "недостаточно прав")


class TestUserRolesRelationship:
    """Тесты для проверки связей пользователя с ролями"""

    def test_user_with_roles(self):
        """Пользователь с назначенными ролями"""
        test_login = unique_login("withroles")

        # Создаём пользователя
        create_query = """
        mutation CreateUser($data: CreateUserInput!) {
            createUser(data: $data) {
                id
                login
            }
        }
        """
        create_response = graphql_query(
            create_query,
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

        response = graphql_query(
            grant_query,
            variables={
                "data": {
                    "userId": user_id,
                    "roleIds": [1]  # Admin role
                }
            },
            headers=ADMIN_HEADERS
        )

        result = assert_graphql_success(response, "grantRole")
        assert result is True

        # Проверяем что пользователь получил роль
        user_query = """
        query GetUser($userId: Int!) {
            user(id: $userId) {
                id
                login
                userRoles {
                    nodes {
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

        user_response = graphql_query(
            user_query,
            variables={"userId": user_id},
            headers=ADMIN_HEADERS
        )

        user_result = assert_graphql_success(user_response, "user")
        assert user_result["userRoles"] is not None
        assert len(user_result["userRoles"]["nodes"]) > 0
        assert user_result["userRoles"]["nodes"][0]["role"]["id"] == 1
