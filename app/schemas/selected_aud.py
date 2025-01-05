from pydantic import BaseModel
from app.schemas.base import *
from datetime import datetime


class SelectedAuditoryBase(BaseModel):
    auditory_id: str = Field(title="Selected-auditory",
                             description="Selected auditory by user",
                             max_length=50,
                             min_length=1)
    success: bool = Field(title="Selection-status",
                          description="Status of auditory selection")


class SelectedAuditoryIn(SelectedAuditoryBase, UserIdBase):
    pass


class SelectedAuditoryOut(SelectedAuditoryBase, UserIdBase, FromOrmBase):
    visit_date: datetime = Field(description="Date when user selected auditory")
