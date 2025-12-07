"""Шаблон описания стандартных ответов для ручек чтения."""

from typing import Any, Type

from app.schemas import Status


def generate_resp(t: Type) -> dict[int, dict[str, Any]]:
    """Возвращает описание ответов 200/403/500 с моделями для OpenAPI."""
    return {
        500: {
            "model": Status,
            "description": "Server side error",
            "content": {"application/json": {"example": {"status": "Some error"}}},
        },
        403: {
            "model": Status,
            "description": "Api_key validation error",
            "content": {"application/json": {"example": {"status": "no api_key"}}},
        },
        200: {"model": t, "description": "List of found data"},
    }
