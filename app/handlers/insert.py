from os import path

from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def insert_floor_map(
    db: AsyncSession,
    full_file_name: str,
    file_path: str,
    link: str,
) -> int:
    """
    Функция для добавления svg-плана в statics.
    Эта функция добавляет запись о файле в таблицу statics.

    Args:
        db: Сессия базы данных;
        full_file_name: Имя файла с расширением;
        file_path: Путь, по которому сохранен файл;
        link: Ссылка на маршрут для получения файла;

    Returns:
        id вставленной записи.
    """
    file_name, file_extension = path.splitext(full_file_name)

    item = models.Static(
        ext=file_extension.lower().lstrip("."),
        path=file_path,
        name=file_name.lower(),
        link=link,
    )

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item.id
