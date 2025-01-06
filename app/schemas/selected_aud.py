from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SelectedAuditoryBase(BaseModel):
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


class SelectedAuditoryIn(SelectedAuditoryBase):
    pass


class SelectedAuditoryOut(SelectedAuditoryBase):
    visit_date: datetime = Field(description="Date when user selected auditory")
    model_config = ConfigDict(from_attributes=True)
