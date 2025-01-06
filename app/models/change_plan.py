from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from .base import Base
from .plan import Plan
from .user_id import UserId


class ChangePlan(Base):
    __tablename__ = "changed_plans"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    plan_id: str = Column(ForeignKey("plans.id"), nullable=False)

    user: Mapped["UserId"] = relationship()
    plan: Mapped["Plan"] = relationship()
