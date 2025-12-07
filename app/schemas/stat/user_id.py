"""Схемы для работы с идентификаторами пользователей."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserId(BaseModel):
    """Уникальный идентификатор пользователя и дата его создания."""

    user_id: str = Field(
        title="User-id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )
    creation_date: Optional[datetime] = Field(default=None)
    model_config = ConfigDict(from_attributes=True)


class UserIdCheck(BaseModel):
    """Модель для проверки существования user_id."""

    user_id: str = Field(
        title="User-id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )
