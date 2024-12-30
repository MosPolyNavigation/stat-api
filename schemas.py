from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class UUID(BaseModel):
    id: str = Field(title="id",
                    description="Unique user id",
                    min_length=36,
                    max_length=36,
                    pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    creation_date: datetime | None = Field(default=None)
    model_config = ConfigDict(from_attributes=True)


class SiteStat(BaseModel):
    uuid: str = Field(title="User-id",
                      description="User id",
                      min_length=36,
                      max_length=36,
                      pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    endpoint: str | None = Field(title="User-path",
                                 description="Path visited by user",
                                 max_length=100,
                                 default=None)
    model_config = ConfigDict(from_attributes=True)


class Status(BaseModel):
    uuid: str = Field(title="id",
                      description="Unique user id",
                      min_length=36,
                      max_length=36,
                      pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    status: str = Field(title="Procedure-status", description="Status of procedure", default="OK")


class SelectedAuditory(BaseModel):
    auditory: str = Field(title="Selected-auditory",
                          description="Selected auditory by user",
                          max_length=50,
                          min_length=1)
    success: bool = Field(title="Selection-status",
                          description="Status of auditory selection")
    model_config = ConfigDict(from_attributes=True)
