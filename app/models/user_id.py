from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from uuid import uuid4
from .base import Base


class UserId(Base):
    __tablename__ = "user_ids"

    user_id: str = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    creation_date: datetime = Column(DateTime, default=datetime.now, nullable=False)
    sites: Mapped[list["SiteStat"]] = relationship("SiteStat", back_populates="user")
    selected: Mapped[list["SelectAuditory"]] = relationship("SelectAuditory", back_populates="user")
    started_ways: Mapped[list["StartWay"]] = relationship("StartWay", back_populates="user")
    changed_plans: Mapped[list["ChangePlan"]] = relationship("ChangePlan", back_populates="user")
