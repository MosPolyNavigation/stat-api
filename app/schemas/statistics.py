from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Statistics(BaseModel):
    """
    Класс для статистики.

    Этот класс содержит поля, которые необходимы для статистики.

    Attributes:
        unique_visitors: Количество уникальных посетителей.
        visitor_count: Количество посетителей.
        all_visits: Общее количество посещений.
        period: Период, за который собрана статистика.
    """
    unique_visitors: int
    visitor_count: int
    all_visits: int
    period: Optional[tuple[datetime, datetime]]
