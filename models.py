from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from uuid import uuid4
from database import Base


class UserId(Base):
    __tablename__ = "user_ids"

    user_id: str = Column(String(36), primary_key=True, default=str(uuid4()))
    creation_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    sites: Mapped[list["SiteStat"]] = relationship("SiteStat", back_populates="user")
    selected: Mapped[list["SelectAuditory"]] = relationship("SelectAuditory", back_populates="user")


class SiteStat(Base):
    __tablename__ = "site_statistics"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    endpoint: str = Column(String(100), nullable=True)

    user: Mapped["UserId"] = relationship("UserId", back_populates="sites")


class Auditory(Base):
    __tablename__ = "auditories"

    id: str = Column(String(50), primary_key=True)
    selected: Mapped[list["SelectAuditory"]] = relationship("SelectAuditory", back_populates="auditory")


class SelectAuditory(Base):
    __tablename__ = "selected_auditories"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    auditory_id: str = Column(ForeignKey("auditories.id"), nullable=False)
    success: bool = Column(Boolean, default=False, nullable=False)

    user: Mapped["UserId"] = relationship("UserId", back_populates="selected")
    auditory: Mapped["Auditory"] = relationship("Auditory", back_populates="selected")
