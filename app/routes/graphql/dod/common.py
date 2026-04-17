import json
from typing import Optional, TypeVar
from graphql import GraphQLError
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


async def get_or_error(session: AsyncSession, model: type[ModelT], entity_id: int, name: str) -> ModelT:
    instance = await session.get(model, entity_id)
    if instance is None:
        raise GraphQLError(f"Сущность {name} не найдена")
    return instance


def validate_json_array(value: Optional[str], field_name: str) -> str:
    """Валидирует строку как JSON-массив. Если значение None — возвращает '[]'.
    При невалидном значении выбрасывает GraphQLError с кодом BAD_USER_INPUT."""
    if value is None:
        return "[]"
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        raise GraphQLError(
            f"Поле {field_name} содержит невалидный JSON",
            extensions={"code": "BAD_USER_INPUT"},
        )
    if not isinstance(parsed, list):
        raise GraphQLError(
            f"Поле {field_name} должно быть JSON-массивом",
            extensions={"code": "BAD_USER_INPUT"},
        )
    return value
