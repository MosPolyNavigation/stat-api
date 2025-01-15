from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserId(BaseModel):
    """
    Класс для уникального идентификатора пользователя.

    Этот класс содержит поля, которые необходимы для уникального идентификатора пользователя.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
        creation_date: Дата создания.
    """
    user_id: str = Field(title="User-id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    creation_date: Optional[datetime] = Field(default=None)
    model_config = ConfigDict(from_attributes=True)
