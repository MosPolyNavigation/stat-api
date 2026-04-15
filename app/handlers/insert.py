from os import path

from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def insert_floor_map(
    db: AsyncSession,
    full_file_name: str,
    file_path: str,
    link: str,
) -> int:
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
