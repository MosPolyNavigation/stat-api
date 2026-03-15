from sqlalchemy import Select, func, union_all, select, case, String, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from typing import Dict
from datetime import date
from .filter import filter_by_date, filter_by_month, filter_by_year
from app import schemas, models


async def get_endpoint_stats(db: AsyncSession, params: schemas.FilterQuery) -> list[schemas.Statistics]:
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
    period_expr = func.cast(func.date(params.model.visit_date), String)
    unique_visitors_expr = case(
        (func.date(models.UserId.creation_date) == func.date(params.model.visit_date), models.UserId.user_id)
    )

    month_borders = filter_by_month(params)
    if month_borders is not None:
        borders = month_borders
        period_expr = func.substr(func.cast(func.date(params.model.visit_date), String), 1, 7)
        unique_visitors_expr = case(
            (
                func.substr(func.cast(func.date(models.UserId.creation_date), String), 1, 7) == period_expr,
                models.UserId.user_id
            )
        )

    year_borders = filter_by_year(params)
    if year_borders is not None:
        borders = year_borders
        period_expr = func.substr(func.cast(func.date(params.model.visit_date), String), 1, 4)
        unique_visitors_expr = case(
            (
                func.substr(func.cast(func.date(models.UserId.creation_date), String), 1, 4) == period_expr,
                models.UserId.user_id
            )
        )

    query = (
        select(
            period_expr.label("period_str"),
            func.count(params.model.user_id).label("all_visits"),
            func.count(params.model.user_id.distinct()).label("visitor_count"),
            func.count(unique_visitors_expr.distinct()).label("unique_visits")
        ).select_from(params.model)
        .join(models.UserId, params.model.user_id == models.UserId.user_id)
        .group_by(period_expr)
        .order_by(period_expr)
    )
    if borders is not None:
        query = (
            query
            .where(params.model.visit_date >= borders[0])
            .where(params.model.visit_date < borders[1])
        )
    rows = (await db.execute(query)).fetchall()
    if params.start_month is not None and params.end_month is not None:
        stats = [
            schemas.Statistics(
                period=date.fromisoformat(f"{row.period_str}-01"),
                all_visits=row.all_visits,
                visitor_count=row.visitor_count,
                unique_visitors=row.unique_visits
            )
            for row in rows
        ]
        return stats

    if params.start_year is not None and params.end_year is not None:
        stats = [
            schemas.Statistics(
                period=date.fromisoformat(f"{row.period_str}-01-01"),
                all_visits=row.all_visits,
                visitor_count=row.visitor_count,
                unique_visitors=row.unique_visits
            )
            for row in rows
        ]
        return stats

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


async def get_agr_endp_stats(db: AsyncSession, params: schemas.FilterQuery) -> schemas.AggregatedStatistics:
    """
    Функция для получения агрегированной статистики по эндпоинту.

    Эта функция агрегирует результаты за период по эндпоинту.

    Args:
        db: Сессия базы данных;
        params: Параметры фильтрации.

    Returns:
        Агрегированная статистика по эндпоинту.
    """
    stats = await get_endpoint_stats(db, params)

    if not stats:
        return schemas.AggregatedStatistics(
            total_all_visits=0,
            total_unique_visitors=0,
            total_visitor_count=0,
            avg_all_visits_per_day=0.0,
            avg_unique_visitors_per_day=0.0,
            avg_visitor_count_per_day=0.0,
            entries_analized=0
        )

    total_all_visits = sum(stat.all_visits for stat in stats)
    total_unique_visitors = sum(stat.unique_visitors for stat in stats)
    total_visitor_count = sum(stat.visitor_count for stat in stats)
    entries_count = len(stats)

    avg_all_visits = round(total_all_visits / entries_count, 1)
    avg_unique_visitors = round(total_unique_visitors / entries_count, 1)
    avg_visitor_count = round(total_visitor_count / entries_count, 1)

    return schemas.AggregatedStatistics(
        total_all_visits=total_all_visits,
        total_unique_visitors=total_unique_visitors,
        total_visitor_count=total_visitor_count,
        avg_all_visits_per_day=avg_all_visits,
        avg_unique_visitors_per_day=avg_unique_visitors,
        avg_visitor_count_per_day=avg_visitor_count,
        entries_analized=entries_count
    )


def get_popular_auds_query():
    """
        Query in basis:
        ```sql
            WITH sw AS (
                SELECT start_id, end_id FROM started_ways
            )
            SELECT ID
            FROM (
                SELECT auditory_id AS ID, 1 AS weight
                FROM selected_auditories
                WHERE success = 1

                UNION ALL
                SELECT start_id, 3 FROM sw

                UNION ALL
                SELECT end_id, 3 FROM sw
            ) AS tr
            GROUP BY ID
            ORDER BY SUM(weight) DESC;
        ```
    """
    sw_cte = select(
        models.StartWay.start_id,
        models.StartWay.end_id
    ).cte('sw')

    # Три части UNION ALL
    part1 = select(
        models.SelectAuditory.auditory_id.label('ID'),
        literal(1).label('weight')
    ).where(models.SelectAuditory.success == 1)

    part2 = select(
        sw_cte.c.start_id.label('ID'),
        literal(3).label('weight')
    )

    part3 = select(
        sw_cte.c.end_id.label('ID'),
        literal(3).label('weight')
    )
    return union_all(part1, part2, part3).alias('tr')


async def get_popular_auds(db: AsyncSession):
    union_query = get_popular_auds_query()
    query = select(union_query.c.ID).group_by(union_query.c.ID).order_by(
        func.sum(union_query.c.weight).desc()
    )
    popular = (await db.execute(query)).scalars().all()
    return popular


async def get_popular_auds_with_count(db: AsyncSession):
    union_query = get_popular_auds_query()
    query = select(
        union_query.c.ID,
        func.sum(union_query.c.weight)
    ).group_by(union_query.c.ID).order_by(
        func.sum(union_query.c.weight).desc()
    )
    popular = (await db.execute(query)).scalars().all()
    return with_count
