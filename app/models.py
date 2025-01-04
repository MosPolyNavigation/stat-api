from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from datetime import datetime
from uuid import uuid4

Base = declarative_base()


class UserId(Base):
    __tablename__ = "user_ids"

    user_id: str = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    creation_date: datetime = Column(DateTime, default=datetime.now, nullable=False)
    sites: Mapped[list["SiteStat"]] = relationship("SiteStat", back_populates="user")
    selected: Mapped[list["SelectAuditory"]] = relationship("SelectAuditory", back_populates="user")
    started_ways: Mapped[list["StartWay"]] = relationship("StartWay", back_populates="user")


class SiteStat(Base):
    __tablename__ = "site_statistics"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    endpoint: str = Column(String(100), nullable=True)

    user: Mapped["UserId"] = relationship("UserId", back_populates="sites")


class Auditory(Base):
    __tablename__ = "auditories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
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


class StartWay(Base):
    __tablename__ = "started_ways"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    start_id: Mapped[str] = mapped_column(ForeignKey("auditories.id"), nullable=False)
    end_id: Mapped[str] = mapped_column(ForeignKey("auditories.id"), nullable=False)

    user: Mapped["UserId"] = relationship("UserId", back_populates="started_ways")
    start: Mapped["Auditory"] = relationship("Auditory", foreign_keys=[start_id])
    end: Mapped["Auditory"] = relationship("Auditory", foreign_keys=[end_id])


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    changed: Mapped[list["ChangePlan"]] = relationship("ChangePlan", back_populates="plan")


class ChangePlan(Base):
    __tablename__ = "changed_plans"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    plan_id: str = Column(ForeignKey("plans.id"), nullable=False)

    user: Mapped["UserId"] = relationship("UserId", back_populates="selected")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="changed")
