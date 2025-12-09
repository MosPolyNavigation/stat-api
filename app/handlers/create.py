"""Обработчики создания базовых сущностей, используемые Swagger-эндпоинтами."""

from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, models


async def create_user_id(db: AsyncSession) -> schemas.UserId:
    """
    Создает новую запись пользователя и возвращает его идентификатор.

    Используется в публичных эндпоинтах для выдачи уникального user_id перед работой с сервисом.

    Args:
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        schemas.UserId: Созданный объект пользователя с заполненным идентификатором.
    """
    item = models.UserId()
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
