"""Схемы выбора аудитории пользователем."""

from pydantic import BaseModel, Field


class SelectedAuditoryIn(BaseModel):
    """Входные данные для фиксации выбора аудитории."""

    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )
    auditory_id: str = Field(
        title="Auditory-id",
        description="Auditory id selected by user",
        max_length=50,
        min_length=1,
    )
    success: bool = Field(
        title="Success",
        description="Was route building successful",
    )
