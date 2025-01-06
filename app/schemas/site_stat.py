from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class SiteStatBase(BaseModel):
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
    pass


class SiteStatOut(SiteStatBase):
    visit_date: datetime = Field(description="Date when user visited this endpoint")
    model_config = ConfigDict(from_attributes=True)
