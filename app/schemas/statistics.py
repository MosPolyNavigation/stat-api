"""Схемы агрегированной статистики."""

from datetime import date

from pydantic import BaseModel


class Statistics(BaseModel):
    """Статистика по периоду: пользователи и количество визитов."""

    unique_visitors: int
    visitor_count: int
    all_visits: int
    period: date
