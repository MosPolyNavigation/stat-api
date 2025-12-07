"""Схемы фиксации начала маршрута пользователя."""

from pydantic import BaseModel, Field


class StartWayIn(BaseModel):
    """Входные данные о построении пути между аудиториями."""

    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )
    start_id: str = Field(
        title="Start",
        description="Start auditory",
        max_length=50,
        min_length=1,
    )
    end_id: str = Field(
        title="End",
        description="End auditory",
        max_length=50,
        min_length=1,
    )
    success: bool = Field(
        title="Success",
        description="Was route building successful",
    )
