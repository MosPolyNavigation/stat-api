from pydantic import BaseModel, Field, field_validator
from app.models.review import Problem
from typing import Optional

class ReviewOut(BaseModel):
    """
    Базовый класс для отзыва.

    Этот класс содержит поля содержащие отзыв пользователя.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
        problem: Тип проблемы, с которой столкнулся пользователь.
        text: Содержимое отзыва пользователя.
        image_uri: Ссылка на картинку, загруженную пользователем.
    """
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    problem: Problem = Field(title="problem",
                             description="User problem")
    text: str = Field(title="text",
                      description="User review")
    image_uri: Optional[str] = Field(title="User screenshot")
