"""Обработчики создания базовых сущностей."""

from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


async def create_user_id(db: AsyncSession) -> schemas.UserId:
    """
    Создает новую запись идентификатора пользователя.

    Генерирует UUID на стороне базы, коммитит и возвращает свежую модель.
    """
    item = models.UserId()
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
