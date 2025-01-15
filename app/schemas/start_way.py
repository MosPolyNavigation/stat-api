from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class StartWayBase(BaseModel):
    """
    Базовый класс для начала пути.

    Этот класс содержит поля, которые необходимы для начала пути.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
        start_id: Идентификатор начала пути.
        end_id: Идентификатор конца пути.
    """
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    start_id: str = Field(title="start-of-way",
                          description="Auditory where user starts way",
                          max_length=50,
                          min_length=1,
                          pattern=r"(!?[abvn]d?(-\w+)*)")
    end_id: str = Field(title="end-of-way",
                        description="Auditory where user ends way",
                        max_length=50,
                        min_length=1,
                        pattern=r"(!?[abvn]d?(-\w+)*)")


class StartWayIn(StartWayBase):
    """
    Класс для входных данных начала пути.

    Этот класс наследуется от StartWayBase и не содержит дополнительных полей.
    """
    pass


class StartWayOut(StartWayBase):
    """
    Класс для выходных данных начала пути.

    Этот класс наследуется от StartWayBase и содержит дополнительное поле visit_date.

    Attributes:
        visit_date: Дата, когда пользователь создал путь.
    """
    visit_date: datetime = Field(description="Date when user created way")
    model_config = ConfigDict(from_attributes=True)
