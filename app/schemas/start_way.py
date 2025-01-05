from pydantic import BaseModel
from app.schemas.base import *
from datetime import datetime


class StartWayBase(BaseModel):
    start_id: str = Field(title="start-of-way",
                          description="Auditory where user starts way",
                          max_length=50,
                          min_length=1)
    end_id: str = Field(title="end-of-way",
                        description="Auditory where user ends way",
                        max_length=50,
                        min_length=1)


class StartWayIn(StartWayBase, UserIdBase):
    pass


class StartWayOut(StartWayBase, UserIdBase, FromOrmBase):
    visit_date: datetime = Field(description="Date when user created way")
