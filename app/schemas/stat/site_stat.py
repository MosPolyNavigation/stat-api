"""Схемы статистики посещения сайта."""

from pydantic import BaseModel, Field


class SiteStatIn(BaseModel):
    """Входная модель для фиксации посещения сайта."""

    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )
    endpoint: str = Field(
        title="Endpoint",
        description="Endpoint user visited",
        max_length=100,
        min_length=1,
    )
