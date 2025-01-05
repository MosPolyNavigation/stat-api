from pydantic import BaseModel
from app.schemas.base import *
from datetime import datetime


class ChangePlanBase(BaseModel):
    plan_id: str = Field(title="Changed-plan",
                         description="Changed plan by user",
                         max_length=4,
                         min_length=3)


class ChangePlanIn(ChangePlanBase, UserIdBase):
    pass


class ChangePlanOut(ChangePlanBase, UserIdBase, FromOrmBase):
    visit_date: datetime = Field(description="Date when user changed plan")
