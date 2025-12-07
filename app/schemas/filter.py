"""Схемы фильтров для API и внутренних обработчиков."""

from datetime import date
from enum import Enum
from typing import Optional, Type

from pydantic import BaseModel, Field, computed_field

from app import models


class Filter(BaseModel):
    """Базовый фильтр с необязательным user_id."""

    user_id: Optional[str] = Field(
        default=None,
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )


class TargetEnum(str, Enum):
    """Список целей для сбора статистики."""

    site = "site"
    auds = "auds"
    ways = "ways"
    plans = "plans"


class FilterQuery(BaseModel):
    """Фильтр статистики по цели и интервалу дат."""

    target: TargetEnum = Field(description="Target info")
    start_date: Optional[date] = Field(default=None, description="Date from which filtering begins")
    end_date: Optional[date] = Field(default=None, description="Date on which filtering ends")

    @computed_field
    @property
    def model(self) -> Type[
        models.ChangePlan | models.StartWay | models.SelectAuditory | models.SiteStat
    ]:
        """Возвращает модель SQLAlchemy для выбранной цели статистики."""
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
    """Список поддерживаемых кампусов."""

    BS = "campus_BS"
    AV = "campus_AV"
    PR = "campus_PR"
    M = "campus_M"
    PK = "campus_PK"


class FilterRoute(BaseModel):
    """Параметры построения маршрута."""

    to_p: str = Field()
    from_p: str = Field(...)
    loc: LocationEnum


class DayOfWeek(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"


class FilterSvobodn(BaseModel):
    """Фильтр для поиска свободных аудиторий."""

    start_date: date = Field(description="Date from which filtering begins")
    end_date: Optional[date] = Field(default=None, description="Date on which filtering ends")
    day: Optional[DayOfWeek] = Field(default=None)
    para: Optional[int] = Field(default=None)


class FilterSvobodnForAud(FilterSvobodn):
    """Фильтр свободности по конкретной аудитории."""

    aud_id: str = Field()


class FilterSvobodnForPlan(FilterSvobodn):
    """Фильтр свободности по плану корпуса."""

    plan_id: str = Field()


class FilterSvobodnByCorpus(FilterSvobodn):
    """Фильтр свободности по корпусу."""

    corpus_id: str = Field()


class FilterSvobodnByLocation(FilterSvobodn):
    """Фильтр свободности по локации."""

    loc_id: str = Field()
