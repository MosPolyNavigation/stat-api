from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class Problem(str, Enum):
    def __str__(self):
        return str(self.value)

    PLAN = "plan"
    WORK = "work"
    WAY = "way"
    OTHER = "other"


class ReviewOut(BaseModel):
    """
    Базовый класс для отзыва.

    Этот класс содержит поля содержащие отзыв пользователя.

    Attributes:
        user_id: Уникальный идентификатор пользователя;
        problem_id: Тип проблемы, с которой столкнулся пользователь;
        text: Содержимое отзыва пользователя;
        image_name: Путь до картинки, загруженной пользователем;
        creation_date: Дата создания отзыва.
    """
    client_id: int = Field(title="client_id", description="Client id")
    problem_id: Problem = Field(title="problem",
                                serialization_alias="problem",
                                description="User problem")
    text: str = Field(title="text",
                      description="User review")
    image_name: Optional[str] = Field(title="User screenshot")
    creation_date: datetime = Field(description="Date when review was send")
    model_config = ConfigDict(from_attributes=True)
