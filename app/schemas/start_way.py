from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class StartWayBase(BaseModel):
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    start_id: str = Field(title="start-of-way",
                          description="Auditory where user starts way",
                          max_length=50,
                          min_length=1,
                          pattern=r"(!?[abvn]d?(-\w+)*)")
    end_id: str = Field(title="end-of-way",
                        description="Auditory where user ends way",
                        max_length=50,
                        min_length=1,
                        pattern=r"(!?[abvn]d?(-\w+)*)")


class StartWayIn(StartWayBase):
    pass


class StartWayOut(StartWayBase):
    visit_date: datetime = Field(description="Date when user created way")
    model_config = ConfigDict(from_attributes=True)
