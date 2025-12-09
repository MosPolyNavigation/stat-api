"""Генератор описаний ответов для Swagger."""

from typing import Type, Any

from app.schemas import Status


def generate_resp(t: Type) -> dict[int, dict[str, Any]]:
    """
    Формирует словарь ответов Swagger для эндпоинтов получения данных.

    Args:
        t: Модель успешного ответа.

    Returns:
        dict[int, dict[str, Any]]: Описание ответов 200/403/500.
    """
    return {
        500: {
            'model': Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        403: {
            'model': Status,
            'description': "Api_key validation error",
            'content': {
                "application/json": {
                    "example": {"status": "no api_key"}
                }
            }
        },
        200: {
            'model': t,
            "description": "List of found data"
        }
    }
