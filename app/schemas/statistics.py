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
