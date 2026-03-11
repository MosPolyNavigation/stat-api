from typing import TypeVar
from graphql import GraphQLError
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


async def get_or_error(session: AsyncSession, model: type[ModelT], entity_id: int, name: str) -> ModelT:
    instance = await session.get(model, entity_id)
    if instance is None:
        raise GraphQLError(f"Ð¡ÑƒÑ‰Ð½Ð¾ÑÑ‚ÑŒ {name} Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð°")
    return instance

