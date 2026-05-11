import uuid

from app.tests.base import client

GRAPHQL_ENDPOINT = "/api/graphql"


def graphql_query(query: str, variables: dict = None, headers: dict = None):
    """Хелпер для выполнения GraphQL-запросов."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables  # noqa

    response = client.post(
        GRAPHQL_ENDPOINT,
        headers=headers or {},
        json=payload
    )
    return {
        "status_code": response.status_code,
        "data": response.json()
    }


def assert_graphql_success(response: dict, field_name: str):
    """Проверяет успешный GraphQL-ответ без ошибок."""
    assert response["status_code"] == 200
    assert "errors" not in response["data"] or not response["data"].get("errors")
    assert response["data"].get("data") is not None
    result = response["data"]["data"].get(field_name)
    assert result is not None, f"Field '{field_name}' not found in response"
    return result


def assert_graphql_error(response: dict, error_substring: str):
    """Проверяет наличие GraphQL-ошибки с ожидаемым текстом."""
    assert response["status_code"] == 200
    assert "errors" in response["data"]
    assert len(response["data"]["errors"]) > 0
    error_message = response["data"]["errors"][0]["message"].lower()
    assert error_substring.lower() in error_message
    return response["data"]["errors"][0]


def unique_login(base="testuser"):
    """Генерирует уникальный логин для изоляции тестов"""
    return f"{base}_{uuid.uuid4().hex[:8]}"
