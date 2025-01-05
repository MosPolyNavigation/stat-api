from pydantic import BaseModel
from app.schemas.base import *
from datetime import datetime
from typing import Optional


class UserId(BaseModel, UserIdBase, FromOrmBase):
    creation_date: Optional[datetime] = Field(default=None)
