from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SiteStatIn(BaseModel):
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


class SiteStatOut(BaseModel):
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
