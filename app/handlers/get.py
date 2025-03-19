from sqlalchemy import Select, and_, column, func, union_all
from sqlalchemy.orm import Session, aliased

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

def get_popular_auds_query():
    """
        Query in basis:
        ```sql
            SELECT ID from
              (SELECT auditory_id as ID, count(*) as CNT from selected_auditories where success=1 group by auditory_id UNION ALL
              SELECT start_id as ID, count(*)*3 as CNT from started_ways group by start_id UNION ALL
              SELECT end_id as ID, count(*)*3 as CNT from started_ways group by end_id) as tr
            GROUP BY ID
            ORDER BY SUM(CNT) DESC;
        ```
    """
    return aliased(
        union_all(
            Select(
                models.SelectAuditory.auditory_id.label('ID'),
                func.count().label('CNT'))
            .select_from(models.SelectAuditory)
            .filter_by(success=True)
            .group_by(models.SelectAuditory.auditory_id.label('ID')),
            Select(models.StartWay.start_id.label('ID'),
                   func.count().label('CNT') * 3)
            .select_from(models.StartWay)
            .group_by(models.StartWay.start_id.label('ID')),
            Select(models.StartWay.end_id.label('ID'),
                   func.count().label('CNT') * 3)
            .select_from(models.StartWay)
            .group_by(models.StartWay.end_id.label('ID'))
        ).alias('tr')
    )

async def get_popular_auds(db: Session):
    tr = get_popular_auds_query()
    query = (Select(tr.c.ID)
             .select_from(tr)
             .group_by(tr.c.ID)
             .order_by(func.sum(tr.c.CNT).desc()))
    return db.execute(query).scalars().all()

async def get_popular_auds_with_count(db: Session):
    tr = get_popular_auds_query()
    query = (Select(tr.c.ID, func.sum(tr.c.CNT))
             .select_from(tr)
             .group_by(tr.c.ID)
             .order_by(func.sum(tr.c.CNT).desc()))
    return db.execute(query).fetchall()
