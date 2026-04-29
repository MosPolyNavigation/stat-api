from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, models


async def create_user_id(db: AsyncSession) -> schemas.UserId:
    """
    Функция для создания уникального идентификатора пользователя.

    Эта функция создает уникальный идентификатор пользователя
    и добавляет его в базу данных.

    Args:
        db: Сессия базы данных.

    Returns:
        Созданный уникальный идентификатор пользователя.
    """
    item = models.ClientId()
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return schemas.UserId(user_id=item.ident, creation_date=item.creation_date)


async def create_client_id(db: AsyncSession) -> schemas.ClientIdentResponse:
    item = models.ClientId()
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return schemas.ClientIdentResponse(ident=item.ident)
