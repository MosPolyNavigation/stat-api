from pydantic import BaseModel, Field, ConfigDict
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
        image_id: Путь до картинку, загруженную пользователем.
        image_ext: Расширение файла.
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
    image_id: Optional[str] = Field(title="User screenshot")
    image_ext: Optional[str] = Field(title="User screenshot")
    model_config = ConfigDict(from_attributes=True)
