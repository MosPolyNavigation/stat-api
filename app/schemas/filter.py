from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Filter(BaseModel):
    """
    Класс для фильтра.

    Этот класс наследуется от BaseModel
    и содержит поле user_id.

    Attributes:
        user_id: Уникальный идентификатор пользователя.
    """

    user_id: Optional[str] = Field(
        default=None,
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )


class LocationEnum(str, Enum):
    """
    Enum-класс для выбора локации.

    Attributes:
        BS: Кампус на Большой Семеновской;
        AV: Кампус на Автозаводской;
        PR: Кампус на Прянишникова;
        M: Кампус на Михалковской;
        PK: Кампус на Павла Корчагина.
    """

    BS = "campus_BS"
    AV = "campus_AV"
    PR = "campus_PR"
    M = "campus_M"
    PK = "campus_PK"


class FilterRoute(BaseModel):
    """Схема фильтра для поиска маршрута."""

    to_p: str = Field()
    from_p: str = Field(...)
    loc: LocationEnum


class DayOfWeek(str, Enum):
    """Дни недели для фильтрации расписания."""

    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"


class FilterSvobodn(BaseModel):
    """
    Фильтр свободных аудиторий.

    Attributes:
        start_date: Дата начала периода;
        end_date: Дата конца периода;
        day: День недели;
        para: Номер пары.
    """

    start_date: date = Field(description="Date from which filtering begins")
    end_date: Optional[date] = Field(
        default=None,
        description="Date on which filtering ends",
    )
    day: Optional[DayOfWeek] = Field(default=None)
    para: Optional[int] = Field(default=None)


class FilterSvobodnForAud(FilterSvobodn):
    """Фильтр свободных аудиторий по аудитории."""

    aud_id: str = Field()


class FilterSvobodnForPlan(FilterSvobodn):
    """Фильтр свободных аудиторий по плану."""

    plan_id: str = Field()


class FilterSvobodnByCorpus(FilterSvobodn):
    """Фильтр свободных аудиторий по корпусу."""

    corpus_id: str = Field()


class FilterSvobodnByLocation(FilterSvobodn):
    """Фильтр свободных аудиторий по локации."""

    loc_id: str = Field()
