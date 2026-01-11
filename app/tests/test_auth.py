"""Тесты для эндпоинтов аутентификации /api/auth"""

import pytest
import uuid
from .base import client

# Токен администратора из base.py (пользователь с полными правами)
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def unique_login(base="testuser"):
    """Генерирует уникальный логин для изоляции тестов"""
    return f"{base}_{uuid.uuid4().hex[:8]}"


class TestAuthToken:
    """Тесты для POST /api/auth/token - получение токена аутентификации"""

    def test_200_login_success(self):
        """Успешная аутентификация с корректными учетными данными"""
        # Создаем тестового пользователя для проверки логина
        test_login = unique_login("logintest")
        client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": test_login,
                "password": "testpass123",
                "is_active": True
            }
        )

        # Проверяем логин
        response = client.post(
            "/api/auth/token",
            data={
                "username": test_login,
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0  # Проверяем что токен не пустой

    def test_400_login_wrong_password(self):
        """Ошибка при неверном пароле"""
        response = client.post(
            "/api/auth/token",
            data={
                "username": "admin",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "некорректный" in data["detail"].lower() or "incorrect" in data["detail"].lower()

    def test_400_login_nonexistent_user(self):
        """Ошибка при попытке войти с несуществующим пользователем"""
        response = client.post(
            "/api/auth/token",
            data={
                "username": "nonexistent_user_12345",
                "password": "anypassword"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_422_login_missing_username(self):
        """Ошибка валидации при отсутствии username"""
        response = client.post(
            "/api/auth/token",
            data={
                "password": "somepassword"
            }
        )
        assert response.status_code == 422

    def test_422_login_missing_password(self):
        """Ошибка валидации при отсутствии password"""
        response = client.post(
            "/api/auth/token",
            data={
                "username": "admin"
            }
        )
        assert response.status_code == 422

    def test_200_login_inactive_user(self):
        """Проверка, что неактивный пользователь может получить токен, но не может использовать его"""
        # Создаем неактивного пользователя
        login = unique_login("inactive")
        create_response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": login,
                "password": "testpass123",
                "is_active": False
            }
        )
        assert create_response.status_code == 201

        # Пытаемся получить токен
        login_response = client.post(
            "/api/auth/token",
            data={
                "username": login,
                "password": "testpass123"
            }
        )
        # Токен должен выдаться
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Но при попытке использовать токен для доступа к /me должна быть ошибка
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Неактивный пользователь не может использовать API (может быть 400 или 401)
        assert me_response.status_code in [400, 401]


class TestAuthMe:
    """Тесты для GET /api/auth/me - получение информации о текущем пользователе"""

    def test_200_me_success(self):
        """Успешное получение информации о текущем пользователе"""
        response = client.get("/api/auth/me", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "login" in data
        assert "is_active" in data
        assert data["login"] == "admin"
        assert data["is_active"] is True
        # Проверяем наличие прав
        assert "rights_by_goals" in data
        assert isinstance(data["rights_by_goals"], dict)

    def test_200_me_has_correct_rights_structure(self):
        """Проверка, что права возвращаются в правильной структуре"""
        response = client.get("/api/auth/me", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        rights = data["rights_by_goals"]

        # Проверяем, что это словарь, где ключи - цели, а значения - массивы прав
        assert isinstance(rights, dict)
        for goal_name, rights_list in rights.items():
            assert isinstance(goal_name, str)
            assert isinstance(rights_list, list)
            assert all(isinstance(right, str) for right in rights_list)

    def test_401_me_no_token(self):
        """Ошибка при отсутствии токена"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_401_me_invalid_token(self):
        """Ошибка при невалидном токене"""
        headers = {"Authorization": "Bearer invalid-token-xyz"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

    def test_401_me_malformed_header(self):
        """Ошибка при неправильном формате заголовка авторизации"""
        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

    def test_200_me_returns_fresh_data(self):
        """Проверка, что /me возвращает актуальные данные после изменений"""
        # Создаем нового пользователя
        login = unique_login("testfresh")
        create_response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": login,
                "password": "password123",
                "is_active": True
            }
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Получаем токен для этого пользователя
        token_response = client.post(
            "/api/auth/token",
            data={
                "username": login,
                "password": "password123"
            }
        )
        assert token_response.status_code == 200
        user_token = token_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Проверяем начальный статус
        me_response = client.get("/api/auth/me", headers=user_headers)
        assert me_response.status_code == 200
        assert me_response.json()["is_active"] is True

        # Деактивируем пользователя через админа
        client.patch(
            f"/api/users/{user_id}",
            headers=ADMIN_HEADERS,
            data={"is_active": False}
        )

        # Пытаемся получить /me - должна быть ошибка, т.к. пользователь неактивен
        me_after_deactivate = client.get("/api/auth/me", headers=user_headers)
        assert me_after_deactivate.status_code in [400, 401]  # Деактивированный пользователь


class TestAuthChangePassword:
    """Тесты для POST /api/auth/change-pass - смена собственного пароля"""

    def test_200_change_own_password_success(self):
        """Успешная смена собственного пароля"""
        # Создаём пользователя
        login = unique_login("ownpasschange")
        client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": login,
                "password": "oldpassword123",
                "is_active": True
            }
        )

        # Получаем токен
        token_response = client.post(
            "/api/auth/token",
            data={
                "username": login,
                "password": "oldpassword123"
            }
        )
        assert token_response.status_code == 200
        user_token = token_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Меняем свой пароль
        response = client.post(
            "/api/auth/change-pass",
            headers=user_headers,
            data={
                "old_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "изменён" in data["message"].lower()

        # Проверяем что можем войти с новым паролем
        new_login_response = client.post(
            "/api/auth/token",
            data={
                "username": login,
                "password": "newpassword456"
            }
        )
        assert new_login_response.status_code == 200
        assert "access_token" in new_login_response.json()

        # Проверяем что старый пароль не работает
        old_login_response = client.post(
            "/api/auth/token",
            data={
                "username": login,
                "password": "oldpassword123"
            }
        )
        assert old_login_response.status_code == 400

    def test_400_change_own_password_wrong_old_password(self):
        """Ошибка при неверном текущем пароле"""
        # Создаём пользователя
        login = unique_login("wrongoldpass")
        client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": login,
                "password": "correctpassword",
                "is_active": True
            }
        )

        # Получаем токен
        token_response = client.post(
            "/api/auth/token",
            data={
                "username": login,
                "password": "correctpassword"
            }
        )
        user_token = token_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Пытаемся изменить пароль с неверным старым паролем
        response = client.post(
            "/api/auth/change-pass",
            headers=user_headers,
            data={
                "old_password": "wrongoldpassword",
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "неверный" in data["detail"].lower()

    def test_401_change_own_password_no_token(self):
        """Ошибка при отсутствии токена аутентификации"""
        response = client.post(
            "/api/auth/change-pass",
            data={
                "old_password": "oldpass",
                "new_password": "newpass"
            }
        )
        assert response.status_code == 401

    def test_422_change_own_password_missing_old_password(self):
        """Ошибка валидации при отсутствии старого пароля"""
        response = client.post(
            "/api/auth/change-pass",
            headers=ADMIN_HEADERS,
            data={
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == 422

    def test_422_change_own_password_missing_new_password(self):
        """Ошибка валидации при отсутствии нового пароля"""
        response = client.post(
            "/api/auth/change-pass",
            headers=ADMIN_HEADERS,
            data={
                "old_password": "oldpassword123"
            }
        )
        assert response.status_code == 422

    def test_422_change_own_password_missing_both_passwords(self):
        """Ошибка валидации при отсутствии обоих паролей"""
        response = client.post(
            "/api/auth/change-pass",
            headers=ADMIN_HEADERS,
            data={}
        )
        assert response.status_code == 422
