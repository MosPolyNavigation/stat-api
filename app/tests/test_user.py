"""Тесты для GraphQL эндпоинтов управления пользователями"""

import pytest
import uuid
from .base import client

# Токен администратора из base.py (пользователь с полными правами)
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

# GraphQL endpoint
GRAPHQL_ENDPOINT = "/api/graphql"


def unique_login(base="testuser"):
    """Генерирует уникальный логин для изоляции тестов"""
    return f"{base}_{uuid.uuid4().hex[:8]}"


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
                "pagination": {"limit": 10, "offset": 0},
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
            variables={"filter": {"login": test_login}},
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
            variables={"filter": {"isActive": True}},
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
            variables={"pagination": {"limit": 1, "offset": 0}},
            headers=ADMIN_HEADERS
        )
        result1 = assert_graphql_success(response1, "users")
        
        # Вторая страница
        response2 = graphql_query(
            query,
            variables={"pagination": {"limit": 1, "offset": 1}},
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
            users(pagination: {limit: 1}) {
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
            user(userId: $userId) {
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
        query GetUser($userId: Int!) {
            user(userId: $userId) {
                id
                login
            }
        }
        """
        
        response = graphql_query(
            query,
            variables={"userId": 999999},
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
        create_response = graphql_query(
            create_query,
            variables={"data": {"login": test_login, "password": "pass123", "isActive": True}},
            headers=ADMIN_HEADERS
        )
        user_id = create_response["data"]["data"]["createUser"]["id"]
        
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
            users(pagination: {limit: 10}) {
                nodes {
                    id
                    login
                }
            }
        }
        """
        
        response = graphql_query(query, headers=user_headers)
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
        create_response = graphql_query(
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
            updateUser(userId: $userId, data: $data) {
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
            updateUser(userId: $userId, data: $data) {
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
            updateUser(userId: $userId, data: $data) {
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
            updateUser(userId: $userId, data: $data) {
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
        create_response = graphql_query(
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
            updateUser(userId: $userId, data: $data) {
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
            deleteUser(userId: $userId) {
                success
                message
                deletedId
            }
        }
        """
        
        response = graphql_query(
            delete_query,
            variables={"userId": user_id},
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "deleteUser")
        assert result["success"] is True
        assert result["deletedId"] == user_id
        assert "удалён" in result["message"].lower()
        
        # Проверяем что пользователь действительно удалён
        get_query = """
        query GetUser($userId: Int!) {
            user(userId: $userId) {
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
            deleteUser(userId: $userId) {
                success
                message
            }
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
            deleteUser(userId: $userId) {
                success
                message
            }
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
        create_response = graphql_query(
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
            deleteUser(userId: $userId) {
                success
                message
            }
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
            changeUserPassword(data: $data) {
                success
                message
                userId
            }
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
        assert result["success"] is True
        assert result["userId"] == user_id
        assert "изменён" in result["message"].lower()
        
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
            changeUserPassword(data: $data) {
                success
                message
            }
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
            changeUserPassword(data: $data) {
                success
                message
            }
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
        
        assert_graphql_error(response, "нельзя изменить пароль самого себя")

    def test_change_user_password_not_found(self):
        """Пользователь не найден"""
        change_query = """
        mutation ChangeUserPassword($data: ChangeUserPasswordInput!) {
            changeUserPassword(data: $data) {
                success
                message
            }
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
        create_response = graphql_query(
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
            changeUserPassword(data: $data) {
                success
                message
            }
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
            grantRole(data: $data) {
                success
                message
                user {
                    id
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
            variables={
                "data": {
                    "userId": user_id,
                    "roleIds": [1]  # Admin role
                }
            },
            headers=ADMIN_HEADERS
        )
        
        result = assert_graphql_success(response, "grantRole")
        assert result["success"] is True
        assert result["user"]["roles"] is not None
        assert len(result["user"]["roles"]) > 0
        
        # Проверяем что пользователь получил роль
        user_query = """
        query GetUser($userId: Int!) {
            user(userId: $userId) {
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
        """
        
        user_response = graphql_query(
            user_query,
            variables={"userId": user_id},
            headers=ADMIN_HEADERS
        )
        
        user_result = assert_graphql_success(user_response, "user")
        assert user_result["roles"] is not None
        assert len(user_result["roles"]) > 0
        assert user_result["roles"][0]["role"]["id"] == 1
