from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Filter(BaseModel):
    user_id: Optional[str] = Field(
        default=None,
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )


class TargetEnum(str, Enum):
    site = "site"
    auds = "auds"
    ways = "ways"
    plans = "plans"


class FilterQuery(BaseModel):
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
    BS = "campus_BS"
    AV = "campus_AV"
    PR = "campus_PR"
    M = "campus_M"
    PK = "campus_PK"


class FilterRoute(BaseModel):
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
    start_date: date = Field(description="Date from which filtering begins")
    end_date: Optional[date] = Field(
        default=None,
        description="Date on which filtering ends",
    )
    day: Optional[DayOfWeek] = Field(default=None)
    para: Optional[int] = Field(default=None)


class TgFilterQuery(BaseModel):
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
    aud_id: str = Field()


class FilterSvobodnForPlan(FilterSvobodn):
    plan_id: str = Field()


class FilterSvobodnByCorpus(FilterSvobodn):
    corpus_id: str = Field()


class FilterSvobodnByLocation(FilterSvobodn):
    loc_id: str = Field()
