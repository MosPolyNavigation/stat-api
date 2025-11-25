from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app import models


async def update_floor_map(
    db: AsyncSession,
    id: int,
    file_path: str
):
    """
    Функция для обновления карты этажа.

    Эта функция карту карту этажа в базе данных.

    Args:
        db: Сессия базы данных;
        id: Идентификатор карты этажа;
        file_path: Путь, по которому был сохранен файл.
    """

    querry = (
        update(models.FloorMap)
        .where(models.FloorMap.id == id)
        .values(file_path=file_path)
    )

    await db.execute(querry)
    await db.commit()
