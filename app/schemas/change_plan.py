from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ChangePlanBase(BaseModel):
    """
    Базовый класс для изменения плана.

    Этот класс содержит поля, которые необходимы для изменения плана.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
        plan_id: Идентификатор измененного плана.
    """
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    plan_id: str = Field(title="Changed-plan",
                         description="Changed plan by user",
                         max_length=4,
                         min_length=3,
                         pattern=r"([ABVN]D?-\d)")


class ChangePlanIn(ChangePlanBase):
    """
    Класс для входных данных изменения плана.

    Этот класс наследуется от ChangePlanBase и не содержит дополнительных полей.
    """
    pass


class ChangePlanOut(ChangePlanBase):
    """
    Класс для выходных данных изменения плана.

    Этот класс наследуется от ChangePlanBase и содержит дополнительное поле visit_date.

    Attributes:
        visit_date: Дата, когда пользователь изменил план.
    """
    visit_date: datetime = Field(description="Date when user changed plan")
    model_config = ConfigDict(from_attributes=True)
