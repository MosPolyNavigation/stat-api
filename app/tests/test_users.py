"""Тесты для эндпоинтов управления пользователями /api/users"""

import pytest
import uuid
from .base import client

# Токен администратора из base.py (пользователь с полными правами)
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def unique_login(base="testuser"):
    """Генерирует уникальный логин для изоляции тестов"""
    return f"{base}_{uuid.uuid4().hex[:8]}"


class TestGetUsers:
    """Тесты для GET /api/users - получение списка пользователей"""

    def test_200_get_users_success(self):
        """Успешное получение списка пользователей с правами"""
        response = client.get("/api/users", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data  # fastapi-pagination возвращает items
        assert "total" in data
        assert len(data["items"]) >= 1  # Как минимум админ должен быть

    def test_401_get_users_no_token(self):
        """Ошибка при отсутствии токена аутентификации"""
        response = client.get("/api/users")
        assert response.status_code == 401

    def test_401_get_users_invalid_token(self):
        """Ошибка при неверном токене"""
        headers = {"Authorization": "Bearer invalid-token-12345"}
        response = client.get("/api/users", headers=headers)
        assert response.status_code == 401

    def test_pagination_works(self):
        """Проверка работы пагинации"""
        # Создадим несколько пользователей сначала
        for i in range(3):
            client.post(
                "/api/users",
                headers=ADMIN_HEADERS,
                data={
                    "login": unique_login("pagtest"),
                    "password": "password123",
                    "is_active": True
                }
            )

        # Проверяем пагинацию
        response = client.get("/api/users?page=1&size=2", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2


class TestGetUserById:
    """Тесты для GET /api/users/{user_id} - получение конкретного пользователя"""

    def test_200_get_user_by_id_success(self):
        """Успешное получение пользователя по ID"""
        # Пользователь с ID=1 (admin) существует из base.py
        response = client.get("/api/users/1", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "login" in data
        assert data["login"] == "admin"
        assert "is_active" in data

    def test_404_get_user_not_found(self):
        """Ошибка 404 при запросе несуществующего пользователя"""
        response = client.get("/api/users/99999", headers=ADMIN_HEADERS)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "не найден" in data["detail"].lower()

    def test_401_get_user_no_token(self):
        """Ошибка при отсутствии токена"""
        response = client.get("/api/users/1")
        assert response.status_code == 401

    def test_422_get_user_invalid_id(self):
        """Ошибка валидации при невалидном ID"""
        response = client.get("/api/users/invalid", headers=ADMIN_HEADERS)
        assert response.status_code == 422


class TestCreateUser:
    """Тесты для POST /api/users - создание нового пользователя"""

    def test_201_create_user_success(self):
        """Успешное создание пользователя"""
        login = unique_login("newuser")
        response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": login,
                "password": "securepass123",
                "is_active": True
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["login"] == login
        assert data["is_active"] is True

    def test_400_create_user_duplicate_login(self):
        """Ошибка при попытке создать пользователя с существующим логином"""
        login = unique_login("duplicate")
        # Создаём пользователя
        client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": login,
                "password": "pass123",
                "is_active": True
            }
        )

        # Пытаемся создать ещё раз с тем же логином
        response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": login,
                "password": "anotherpass",
                "is_active": True
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "существует" in data["detail"].lower()

    def test_422_create_user_missing_login(self):
        """Ошибка валидации при отсутствии обязательного поля login"""
        response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "password": "pass123"
            }
        )
        assert response.status_code == 422

    def test_422_create_user_missing_password(self):
        """Ошибка валидации при отсутствии обязательного поля password"""
        response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": "usernopass"
            }
        )
        assert response.status_code == 422

    def test_201_create_user_default_active(self):
        """Создание пользователя без указания is_active (должен быть True по умолчанию)"""
        response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": unique_login("defaultactive"),
                "password": "pass123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_active"] is True

    def test_401_create_user_no_token(self):
        """Ошибка при отсутствии токена"""
        response = client.post(
            "/api/users",
            data={
                "login": "unauthorized",
                "password": "pass123"
            }
        )
        assert response.status_code == 401


class TestUpdateUser:
    """Тесты для PATCH /api/users/{user_id} - обновление пользователя"""

    def test_200_update_user_password(self):
        """Успешное обновление пароля пользователя"""
        # Создаём пользователя
        create_response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": unique_login("usertoupdate"),
                "password": "oldpass",
                "is_active": True
            }
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Обновляем пароль
        response = client.patch(
            f"/api/users/{user_id}",
            headers=ADMIN_HEADERS,
            data={
                "password": "newpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "пароль" in data["message"].lower()

    def test_200_update_user_is_active(self):
        """Успешное обновление статуса is_active"""
        # Создаём пользователя для тестирования (НЕ админа!)
        create_response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": unique_login("active_test"),
                "password": "pass123",
                "is_active": True
            }
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Меняем статус на False
        response = client.patch(
            f"/api/users/{user_id}",
            headers=ADMIN_HEADERS,
            data={
                "is_active": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "статус" in data["message"].lower()

    def test_200_update_user_both_fields(self):
        """Обновление и пароля, и статуса одновременно"""
        # Создаём пользователя для тестирования
        create_response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": unique_login("testuser_both"),
                "password": "oldpass",
                "is_active": False  # Создаём неактивным
            }
        )
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # Обновим и пароль, и статус (делаем активным и меняем пароль)
        response = client.patch(
            f"/api/users/{user_id}",
            headers=ADMIN_HEADERS,
            data={
                "password": "newpass456",
                "is_active": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "пароль" in data["message"].lower()
        assert "статус" in data["message"].lower()

    def test_200_update_user_no_changes(self):
        """Запрос на обновление без изменений"""
        response = client.patch(
            "/api/users/1",
            headers=ADMIN_HEADERS,
            data={}
        )
        assert response.status_code == 200
        data = response.json()
        assert "изменений не было" in data["message"].lower()

    def test_404_update_user_not_found(self):
        """Ошибка 404 при попытке обновить несуществующего пользователя"""
        response = client.patch(
            "/api/users/99999",
            headers=ADMIN_HEADERS,
            data={
                "password": "newpass"
            }
        )
        assert response.status_code == 404
        data = response.json()
        assert "не найден" in data["detail"].lower()

    def test_401_update_user_no_token(self):
        """Ошибка при отсутствии токена"""
        response = client.patch(
            "/api/users/1",
            data={"password": "newpass"}
        )
        assert response.status_code == 401

    def test_422_update_user_invalid_id(self):
        """Ошибка валидации при невалидном ID"""
        response = client.patch(
            "/api/users/notanumber",
            headers=ADMIN_HEADERS,
            data={"password": "newpass"}
        )
        assert response.status_code == 422


class TestDeleteUser:
    """Тесты для DELETE /api/users/{user_id} - удаление пользователя"""

    def test_200_delete_user_success(self):
        """Успешное удаление пользователя"""
        # Создаём пользователя для удаления
        create_response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": unique_login("usertodelete"),
                "password": "pass123",
                "is_active": True
            }
        )
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # Удаляем пользователя
        delete_response = client.delete(f"/api/users/{user_id}", headers=ADMIN_HEADERS)
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert "message" in data
        assert user_id == data["user_id"]

        # Проверяем что пользователь действительно удалён
        get_response = client.get(f"/api/users/{user_id}", headers=ADMIN_HEADERS)
        assert get_response.status_code == 404

    def test_200_delete_user_returns_message(self):
        """Проверка, что при удалении возвращается сообщение с ID"""
        # Создаём пользователя
        create_response = client.post(
            "/api/users",
            headers=ADMIN_HEADERS,
            data={
                "login": unique_login("userfordeletion"),
                "password": "pass123"
            }
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Удаляем пользователя
        response = client.delete(f"/api/users/{user_id}", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert data["user_id"] == user_id

    def test_404_delete_user_not_found(self):
        """Ошибка 404 при попытке удалить несуществующего пользователя"""
        response = client.delete("/api/users/99999", headers=ADMIN_HEADERS)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        # Проверяем что в сообщении есть упоминание о ненайденном пользователе
        assert "найден" in data["detail"].lower() or "not found" in data["detail"].lower()

    def test_401_delete_user_no_token(self):
        """Ошибка при отсутствии токена"""
        response = client.delete("/api/users/1")
        assert response.status_code == 401

    def test_422_delete_user_invalid_id(self):
        """Ошибка валидации при невалидном ID"""
        response = client.delete("/api/users/invalid", headers=ADMIN_HEADERS)
        assert response.status_code == 422
