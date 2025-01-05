from pydantic import BaseModel, Field, computed_field
from typing import Optional, Type
from datetime import date
from app import models
from enum import Enum


class FilterBase(BaseModel):
    api_key: str = Field(min_length=64,
                         max_length=64,
                         description="Api key for statistics gathering",
                         pattern=r"[a-f0-9]{64}")


class Filter(FilterBase):
    user_id: str | None = Field(default=None,
                                title="id",
                                description="Unique user id",
                                min_length=36,
                                max_length=36,
                                pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")


class TargetEnum(str, Enum):
    site = 'site'
    auds = 'auds'
    ways = 'ways'
    plans = 'plans'


class FilterQuery(FilterBase):
    target: TargetEnum = Field(description="Target info")
    start_date: Optional[date] = Field(default=None, description="Date from which filtering begins")
    end_date: Optional[date] = Field(default=None, description="Date on which filtering ends")

    @computed_field
    @property
    def model(self) -> Type[models.ChangePlan | models.StartWay | models.SelectAuditory | models.SiteStat]:
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
