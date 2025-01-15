from sqlalchemy.orm import Session
from app import schemas, models


async def create_user_id(db: Session) -> schemas.UserId:
    """
    Функция для создания уникального идентификатора пользователя.

    Эта функция создает уникальный идентификатор пользователя и добавляет его в базу данных.

    Args:
        db: Сессия базы данных.

    Returns:
        schemas.UserId: Созданный уникальный идентификатор пользователя.
    """
    item = models.UserId()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
