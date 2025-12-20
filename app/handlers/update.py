"""Обработчики обновления данных в базе."""

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app import models


async def update_floor_map(
    db: AsyncSession,
    id: int,
    file_path: str
):
    """
    Обновляет путь к файлу схемы этажа.

    Используется в эндпоинтах загрузки новых планов этажей.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        id: Идентификатор записи в таблице floor_maps.
        file_path: Новый путь до файла изображения.

    """

    querry = (
        update(models.FloorMap)
        .where(models.FloorMap.id == id)
        .values(file_path=file_path)
    )

    await db.execute(querry)
    await db.commit()
