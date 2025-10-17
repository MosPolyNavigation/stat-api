from sqlalchemy import Select, func, union_all, select, case, String
from sqlalchemy.orm import Session, aliased
from datetime import date

from .filter import filter_by_date
from app import schemas, models


async def get_endpoint_stats(db: Session, params: schemas.FilterQuery) -> list[schemas.Statistics]:
    """
    Функция для получения статистики по эндпоинту.

    Эта функция получает статистику по эндпоинту.

    Args:
        db: Сессия базы данных;
        params: Параметры фильтрации.

    Returns:
        Статистика по эндпоинту.
    """
    borders = filter_by_date(params)
    visit_date_expr = func.date(params.model.visit_date)
    visit_date_out_expr = func.cast(visit_date_expr, String)
    query = (
        select(
            visit_date_out_expr.label("period_str"),
            func.count(params.model.user_id).label("all_visits"),
            func.count(params.model.user_id.distinct()).label("visitor_count"),
            func.count(
                case(
                    (func.date(models.UserId.creation_date) == visit_date_expr, models.UserId.user_id)
                ).distinct()
            ).label("unique_visits")
        ).select_from(params.model)
        .join(models.UserId, params.model.user_id == models.UserId.user_id)
        .group_by(visit_date_out_expr)
        .order_by(visit_date_out_expr)
    )
    if borders is not None:
        query = (
            query
            .where(params.model.visit_date >= borders[0])
            .where(params.model.visit_date < borders[1])
        )
    print(query.__str__())
    rows = db.execute(query).fetchall()
    stats = [
        schemas.Statistics(
            period=date.fromisoformat(row.period_str),
            all_visits=row.all_visits,
            visitor_count=row.visitor_count,
            unique_visitors=row.unique_visits
        )
        for row in rows
    ]
    return stats


def get_popular_auds_query():
    """
        Query in basis:
        ```sql
            SELECT ID from (
              SELECT auditory_id as ID, count(*) as CNT
              from selected_auditories
              where success=1
              group by auditory_id
              UNION ALL
              SELECT start_id as ID, count(*)*3 as CNT
              from started_ways
              group by start_id
              UNION ALL
              SELECT end_id as ID, count(*)*3 as CNT
              from started_ways
              group by end_id
            ) as tr
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
