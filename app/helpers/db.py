from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def exists(session: AsyncSession, model: type[T], item_id: int) -> bool:
    return (
        await session.execute(select(model).where(model.id == item_id))
    ).scalar_one_or_none() is not None
