from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class SiteStatBase(BaseModel):
    """
    Базовый класс для статистики сайта.

    Этот класс содержит поля, которые необходимы для статистики сайта.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
        endpoint: Путь, посещенный пользователем.
    """
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    endpoint: Optional[str] = Field(title="User-path",
                                    description="Path visited by user",
                                    max_length=100,
                                    default=None)


class SiteStatIn(SiteStatBase):
    """
    Класс для входных данных статистики сайта.

    Этот класс наследуется от SiteStatBase и не содержит дополнительных полей.
    """
    pass


class SiteStatOut(SiteStatBase):
    """
    Класс для выходных данных статистики сайта.

    Этот класс наследуется от SiteStatBase и содержит дополнительное поле visit_date.

    Attributes:
        visit_date: Дата, когда пользователь посетил этот путь.
    """
    visit_date: datetime = Field(description="Date when user visited this endpoint")
    model_config = ConfigDict(from_attributes=True)
