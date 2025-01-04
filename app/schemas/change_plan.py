from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ChangePlanIn(BaseModel):
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    plan_id: str = Field(title="Changed-plan",
                         description="Changed plan by user",
                         max_length=4,
                         min_length=3)


class SelectedAuditoryOut(BaseModel):
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
    visit_date: datetime = Field(description="Date when user changed plan")
    plan_id: str = Field(title="Changed-auditory",
                         description="Changed plan by user",
                         max_length=4,
                         min_length=3)
    model_config = ConfigDict(from_attributes=True)
