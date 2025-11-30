from typing import TypeVar
from graphql import GraphQLError
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


async def get_or_error(session: AsyncSession, model: type[ModelT], entity_id: int, name: str) -> ModelT:
    instance = await session.get(model, entity_id)
    if instance is None:
        raise GraphQLError(f"Сущность {name} не найдена")
    return instance
