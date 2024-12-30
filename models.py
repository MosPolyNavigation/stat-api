from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from uuid import uuid4
from database import Base


class UUID(Base):
    __tablename__ = "uuids"

    id: str = Column(String(36), primary_key=True, default=str(uuid4()))
    creation_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    sites: Mapped[list["SiteStat"]] = relationship("SiteStat", back_populates="uuid")
    selected: Mapped[list["SelectAuditory"]] = relationship("SelectAuditory", back_populates="uuid")


class SiteStat(Base):
    __tablename__ = "site_statistics"

    id: int = Column(Integer, primary_key=True, index=True)
    uuid_id: str = Column(ForeignKey("uuids.id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    endpoint: str = Column(String(100), default="/", nullable=False)

    uuid: Mapped["UUID"] = relationship("UUID", back_populates="sites")


class Auditory(Base):
    __tablename__ = "auditories"

    id: str = Column(String(50), primary_key=True)
    selected: Mapped[list["SelectAuditory"]] = relationship("SelectAuditory", back_populates="auditory")


class SelectAuditory(Base):
    __tablename__ = "selected_auditories"

    id: int = Column(Integer, primary_key=True, index=True)
    uuid_id: str = Column(ForeignKey("uuids.id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    auditory_id: str = Column(ForeignKey("auditories.id"), nullable=False)
    success: bool = Column(Boolean, default=False, nullable=False)

    uuid: Mapped["UUID"] = relationship("UUID", back_populates="selected")
    auditory: Mapped["Auditory"] = relationship("Auditory", back_populates="selected")
