from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SelectedAuditoryBase(BaseModel):
    """
    Базовый класс для выбранной аудитории.

    Этот класс содержит поля, которые необходимы для выбранной аудитории.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
        auditory_id: Идентификатор выбранной аудитории.
        success: Статус выбора аудитории.
    """
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    auditory_id: str = Field(title="Selected-auditory",
                             description="Selected auditory by user",
                             max_length=50,
                             min_length=1,
                             pattern=r"(!?[abvn]d?(-\w+)*)")
    success: bool = Field(title="Selection-status",
                          description="Status of auditory selection")


class SelectedAuditoryIn(SelectedAuditoryBase):
    """
    Класс для входных данных выбранной аудитории.

    Этот класс наследуется от SelectedAuditoryBase и не содержит дополнительных полей.
    """
    pass


class SelectedAuditoryOut(SelectedAuditoryBase):
    """
    Класс для выходных данных выбранной аудитории.

    Этот класс наследуется от SelectedAuditoryBase и содержит дополнительное поле visit_date.

    Attributes:
        visit_date: Дата, когда пользователь выбрал аудиторию.
    """
    visit_date: datetime = Field(description="Date when user selected auditory")
    model_config = ConfigDict(from_attributes=True)
