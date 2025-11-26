from pydantic import BaseModel, Field, computed_field
from typing import Optional, Type
from datetime import date
from app import models
from enum import Enum


class Filter(BaseModel):
    """
    Класс для фильтра.

    Этот класс наследуется от FilterBase
    и содержит дополнительное поле user_id.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
    """
    user_id: Optional[str] = Field(
        default=None,
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"
    )


class TargetEnum(str, Enum):
    """
    Enum класс для целей фильтрации.

    Этот класс содержит возможные цели фильтрации.

    Attributes:
        site: Цель фильтрации для сайта;
        auds: Цель фильтрации для аудитории;
        ways: Цель фильтрации для путей;
        plans: Цель фильтрации для планов.
    """
    site = 'site'
    auds = 'auds'
    ways = 'ways'
    plans = 'plans'


class FilterQuery(BaseModel):
    """
    Класс для фильтра запроса.

    Этот класс наследуется от FilterBase
    и содержит дополнительные поля target, start_date и end_date.

    Attributes:
        target: Цель фильтрации;
        start_date: дата, с которой начинается фильтрация;
        end_date: дата, на которой заканчивается фильтрация.
    """
    target: TargetEnum = Field(description="Target info")
    start_date: Optional[date] = Field(
        default=None, description="Date from which filtering begins"
    )
    end_date: Optional[date] = Field(
        default=None, description="Date on which filtering ends"
    )

    @computed_field
    @property
    def model(self) -> Type[models.ChangePlan |
                            models.StartWay |
                            models.SelectAuditory |
                            models.SiteStat]:
        """
        Свойство для получения модели.

        Это свойство возвращает модель в зависимости от цели фильтрации.

        Returns:
            Модель.
        """
        if self.target is TargetEnum.plans:
            return models.ChangePlan
        elif self.target is TargetEnum.ways:
            return models.StartWay
        elif self.target is TargetEnum.auds:
            return models.SelectAuditory
        elif self.target is TargetEnum.site:
            return models.SiteStat
        else:
            raise ValueError("no such target")


class LocationEnum(str, Enum):
    """
    Enum класс для целей фильтрации.

    Этот класс содержит возможные цели фильтрации.

    Attributes:
        BS: Выбрать корпус на большой семеновской;
        AV: Выбрать корпус на большой автозаводской;
        PR: Выбрать корпус на прянишникова;
        M: Выбрать корпус на михалковской;
        PK: Выбрать корпус на Павла Корчагина.
    """
    BS = 'campus_BS'
    AV = 'campus_AV'
    PR = 'campus_PR'
    M = 'campus_M'
    PK = 'campus_PK'


class FilterRoute(BaseModel):
    to_p: str = Field()
    from_p: str = Field(...)
    loc: LocationEnum


class DayOfWeek(str, Enum):
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = "wednesday"
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'


class FilterSvobodn(BaseModel):
    start_date: date = Field(
        description="Date from which filtering begins"
    )
    end_date: Optional[date] = Field(
        default=None, description="Date on which filtering ends"
    )
    day: Optional[DayOfWeek] = Field(default=None)
    para: Optional[int] = Field(default=None)


class FilterSvobodnForAud(FilterSvobodn):
    aud_id: str = Field()


class FilterSvobodnForPlan(FilterSvobodn):
    plan_id: str = Field()


class FilterSvobodnByCorpus(FilterSvobodn):
    corpus_id: str = Field()


class FilterSvobodnByLocation(FilterSvobodn):
    loc_id: str = Field()
