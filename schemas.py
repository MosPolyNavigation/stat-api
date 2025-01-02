from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from datetime import datetime
from config import Settings
from typing import Any


class UserId(BaseModel):
    user_id: str = Field(title="User-id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    creation_date: datetime | None = Field(default=None)
    model_config = ConfigDict(from_attributes=True)


class SiteStat(BaseModel):
    user_id: str = Field(title="User-id",
                         description="User id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    endpoint: str | None = Field(title="User-path",
                                 description="Path visited by user",
                                 max_length=100,
                                 default=None)
    model_config = ConfigDict(from_attributes=True)


class SiteStatDB(BaseModel):
    user_id: str = Field(title="User-id",
                         description="User id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    visit_date: datetime = Field(description="Date when user visited this endpoint")
    endpoint: str | None = Field(title="User-path",
                                 description="Path visited by user",
                                 max_length=100,
                                 default=None)
    model_config = ConfigDict(from_attributes=True)


class Status(BaseModel):
    status: str = Field(title="Procedure-status", description="Status of procedure", default="OK")


class SelectedAuditory(BaseModel):
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    auditory_id: str = Field(title="Selected-auditory",
                             description="Selected auditory by user",
                             max_length=50,
                             min_length=1)
    success: bool = Field(title="Selection-status",
                          description="Status of auditory selection")
    model_config = ConfigDict(from_attributes=True)


class SelectedAuditoryDB(BaseModel):
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    visit_date: datetime = Field(description="Date when user selected auditory")
    auditory_id: str = Field(title="Selected-auditory",
                             description="Selected auditory by user",
                             max_length=50,
                             min_length=1)
    success: bool = Field(title="Selection-status",
                          description="Status of auditory selection")
    model_config = ConfigDict(from_attributes=True)


class StatisticsBase(BaseModel):
    api_key: str = Field(min_length=64,
                         max_length=64,
                         description="Api key for statistics gathering",
                         pattern=r"[a-f0-9]{64}")
    page: int | None = Field(default=None, ge=1, description="Page number, starting from 1")
    user_id: str | None = Field(default=None,
                                title="id",
                                description="Unique user id",
                                min_length=36,
                                max_length=36,
                                pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")

    per_page: int | None = Field(default=None, gt=0, le=100, description="Numbers of items per_page")

    @classmethod
    @field_validator('api_key')
    def check_key(cls, v: Any):
        if v != Settings().admin_key:
            raise ValueError("Specified api_key is not present in app")
        return v

    @model_validator(mode='after')
    def check_both(self):
        if (self.page is None) != (self.per_page is None):
            raise ValueError('Both page and per_page must be either set or None')
        return self
