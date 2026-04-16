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


class TargetEnum(str, Enum):
    """
    Enum-класс для целей фильтрации.

    Attributes:
        site: Цель фильтрации для сайта;
        auds: Цель фильтрации для аудиторий;
        ways: Цель фильтрации для маршрутов;
        plans: Цель фильтрации для планов.
    """

    site = "site"
    auds = "auds"
    ways = "ways"
    plans = "plans"


class FilterQuery(BaseModel):
    """
    Класс для фильтра запроса.

    Attributes:
        target: Цель фильтрации;
        start_date: Дата начала фильтрации;
        end_date: Дата окончания фильтрации;
        start_month: Месяц начала фильтрации в формате YYYY-MM;
        end_month: Месяц окончания фильтрации в формате YYYY-MM;
        start_year: Год начала фильтрации в формате YYYY;
        end_year: Год окончания фильтрации в формате YYYY.
    """

    target: TargetEnum = Field(description="Target info")
    start_date: Optional[date] = Field(
        default=None,
        description="Date from which filtering begins",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Date on which filtering ends",
    )
    start_month: Optional[str] = Field(
        default=None,
        description="Month from which filtering begins in YYYY-MM format",
    )
    end_month: Optional[str] = Field(
        default=None,
        description="Month on which filtering ends in YYYY-MM format",
    )
    start_year: Optional[str] = Field(
        default=None,
        description="Year from which filtering begins in YYYY format",
    )
    end_year: Optional[str] = Field(
        default=None,
        description="Year on which filtering ends in YYYY format",
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


class TgFilterQuery(BaseModel):
    """
    Класс для фильтрации статистики телеграм-бота.

    Attributes:
        event_type_id: Идентификатор типа события телеграм-бота;
        is_dod: Признак, что событие относится к DOD-боту;
        start_date: Дата начала фильтрации;
        end_date: Дата окончания фильтрации;
        start_month: Месяц начала фильтрации в формате YYYY-MM;
        end_month: Месяц окончания фильтрации в формате YYYY-MM;
        start_year: Год начала фильтрации в формате YYYY;
        end_year: Год окончания фильтрации в формате YYYY.
    """

    event_type_id: Optional[int] = Field(
        default=None,
        description="Telegram bot event type identifier",
    )
    is_dod: Optional[bool] = Field(
        default=None,
        description="Whether event belongs to DOD bot",
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Date from which filtering begins",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Date on which filtering ends",
    )
    start_month: Optional[str] = Field(
        default=None,
        description="Month from which filtering begins in YYYY-MM format",
    )
    end_month: Optional[str] = Field(
        default=None,
        description="Month on which filtering ends in YYYY-MM format",
    )
    start_year: Optional[str] = Field(
        default=None,
        description="Year from which filtering begins in YYYY format",
    )
    end_year: Optional[str] = Field(
        default=None,
        description="Year on which filtering ends in YYYY format",
    )


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
