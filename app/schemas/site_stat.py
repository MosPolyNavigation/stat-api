from pydantic import BaseModel
from app.schemas.base import *
from datetime import datetime
from typing import Optional


class SiteStatBase(BaseModel):
    endpoint: Optional[str] = Field(title="User-path",
                                    description="Path visited by user",
                                    max_length=100,
                                    default=None)


class SiteStatIn(SiteStatBase, UserIdBase):
    pass


class SiteStatOut(SiteStatBase, UserIdBase, FromOrmBase):
    visit_date: datetime = Field(description="Date when user visited this endpoint")
