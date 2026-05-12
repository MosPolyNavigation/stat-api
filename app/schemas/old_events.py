"""TODO: Удалить как фронты перейдут на новую схему событий"""

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ChangePlanBase(BaseModel):
    """
    Базовый класс для изменения плана.

    Этот класс содержит поля, которые необходимы для изменения плана.

    Attributes:
        user_id: Уникальный идентификатор пользователя;
        plan_id: Идентификатор измененного плана.
    """
    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"
    )
    plan_id: str = Field(
        title="Changed-plan",
        description="Changed plan by user",
        max_length=50,
        min_length=1,
        # pattern=r"([ABVN]D?-\d)"
    )


class ChangePlanIn(ChangePlanBase):
    """
    Класс для входных данных изменения плана.

    Этот класс наследуется от ChangePlanBase
    и не содержит дополнительных полей.
    """
    pass


class SelectedAuditoryBase(BaseModel):
    """
    Базовый класс для выбранной аудитории.

    Этот класс содержит поля, которые необходимы для выбранной аудитории.

    Attributes:
        user_id: Уникальный идентификатор пользователя;
        auditory_id: Идентификатор выбранной аудитории;
        success: Статус выбора аудитории.
    """
    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"
    )
    auditory_id: str = Field(
        title="Selected-auditory",
        description="Selected auditory by user",
        max_length=50,
        min_length=1,
        # pattern=r"(!?[abvn]d?(-\w+)*)"
    )
    success: bool = Field(title="Selection-status",
                          description="Status of auditory selection")


class SelectedAuditoryIn(SelectedAuditoryBase):
    """
    Класс для входных данных выбранной аудитории.

    Этот класс наследуется от SelectedAuditoryBase
    и не содержит дополнительных полей.
    """
    pass


class SiteStatBase(BaseModel):
    """
    Базовый класс для статистики сайта.

    Этот класс содержит поля, которые необходимы для статистики сайта.

    Attributes:
        user_id: Уникальный идентификатор пользователя;
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


class StartWayBase(BaseModel):
    """
    Базовый класс для начала пути.

    Этот класс содержит поля, которые необходимы для начала пути.

    Attributes:
        user_id: Уникальный идентификатор пользователя;
        start_id: Идентификатор начала пути;
        end_id: Идентификатор конца пути;
        success: Успешно ли был построен маршрут.
    """
    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"
    )
    start_id: str = Field(
        title="start-of-way",
        description="Auditory where user starts way",
        max_length=50,
        min_length=1,
        # pattern=r"(!?[abvn]d?(-\w+)*)"
    )
    end_id: str = Field(
        title="end-of-way",
        description="Auditory where user ends way",
        max_length=50,
        min_length=1,
        # pattern=r"(!?[abvn]d?(-\w+)*)"
    )

    success: bool = Field(
        title="Selection-status",
        description="Status of auditory selection"
    )


class StartWayIn(StartWayBase):
    """
    Класс для входных данных начала пути.

    Этот класс наследуется от StartWayBase и не содержит дополнительных полей.
    """
    pass


class UserId(BaseModel):
    """
    Класс для уникального идентификатора пользователя.

    Этот класс содержит поля, которые необходимы для
    уникального идентификатора пользователя.

    Attributes:
        user_id: Уникальный идентификатор пользователя;
        creation_date: Дата создания.
    """
    user_id: str = Field(title="User-id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    creation_date: Optional[datetime] = Field(default=None)
    model_config = ConfigDict(from_attributes=True)


class UserIdCheck(BaseModel):
    """
    Класс для уникального идентификатора пользователя.

    Этот класс содержит поля, которые необходимы для
    уникального идентификатора пользователя.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
    """
    user_id: str = Field(
        title="User-id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"
    )
