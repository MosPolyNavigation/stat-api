"""Схемы отзывов пользователей."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Problem(str, Enum):
    """Типы проблем, о которых сообщают пользователи."""

    def __str__(self):
        return str(self.value)

    PLAN = "plan"
    WORK = "work"
    WAY = "way"
    OTHER = "other"


class ReviewOut(BaseModel):
    """Отзыв пользователя с текстом, проблемой и опциональным изображением."""

    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )
    problem_id: Problem = Field(title="problem", serialization_alias="problem", description="User problem")
    text: str = Field(title="text", description="User review")
    image_name: Optional[str] = Field(title="User screenshot")
    creation_date: datetime = Field(description="Date when review was send")
    model_config = ConfigDict(from_attributes=True)
