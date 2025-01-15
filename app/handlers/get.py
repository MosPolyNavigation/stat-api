from sqlalchemy import Select, and_, column, func
from sqlalchemy.orm import Session
from .filter import filter_by_date
from app import schemas, models


async def get_endpoint_stats(db: Session, params: schemas.FilterQuery):
    """
    Функция для получения статистики по эндпоинту.

    Эта функция получает статистику по эндпоинту.

    Args:
        db: Сессия базы данных.
        params: Параметры фильтрации.

    Returns:
        schemas.Statistics: Статистика по эндпоинту.
    """
    query, borders = filter_by_date(params)
    all_visits = len(db.execute(query).scalars().all())
    unique_query = Select(func.count(models.UserId.user_id)).filter(column("user_id").in_(query))
    visitor_count = db.execute(unique_query).scalar()
    if borders is not None:
        unique_query = unique_query.filter(and_(
            models.UserId.creation_date >= borders[0],
            models.UserId.creation_date <= borders[1]
        ))
    unique_visitors = db.execute(unique_query).scalar()
    return schemas.Statistics(
        unique_visitors=unique_visitors,
        visitor_count=visitor_count,
        all_visits=all_visits,
        period=borders
    )
