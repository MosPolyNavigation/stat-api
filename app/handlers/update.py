"""Обработчики обновления сущностей."""

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def update_floor_map(db: AsyncSession, id: int, file_path: str):
    """Обновляет путь к файлу плана этажа."""
    query = (
        update(models.FloorMap)
        .where(models.FloorMap.id == id)
        .values(file_path=file_path)
    )

    await db.execute(query)
    await db.commit()
