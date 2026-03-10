from pydantic import BaseModel
from datetime import date


class Statistics(BaseModel):
    """
    Класс для статистики.

    Этот класс содержит поля, которые необходимы для статистики.

    Attributes:
        unique_visitors: Количество уникальных посетителей;
        visitor_count: Количество посетителей;
        all_visits: Общее количество посещений;
        period: Дата за которую собрана статистика.
    """
    unique_visitors: int
    visitor_count: int
    all_visits: int
    period: date


class AggregatedStatistics(BaseModel):
    """
    Класс для агрегированной статистики.

    Этот класс содержит поля для агрегированной статистики за период.

    Attributes:
        total_all_visits: Общее количество посещений за период;
        total_unique_visitors: Общее количество уникальных посетителей за период;
        total_visitor_count: Общее количество посетителей за период;
        avg_all_visits_per_day: Среднее количество посещений в день;
        avg_unique_visitors_per_day: Среднее количество уникальных посетителей в день;
        avg_visitor_count_per_day: Среднее количество посетителей в день;
        entries_analized: Количество проанализированных записей.
    """
    total_all_visits: int
    total_unique_visitors: int
    total_visitor_count: int
    avg_all_visits_per_day: float
    avg_unique_visitors_per_day: float
    avg_visitor_count_per_day: float
    entries_analized: int
