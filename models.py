from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from uuid import uuid4
from database import Base


class UUID(Base):
    __tablename__ = "uuids"

    id: str = Column(String(36), primary_key=True, default=str(uuid4()))
    creation_date: datetime = Column(DateTime, default=datetime.now())
    sites: Mapped[list["SiteStat"]] = relationship("SiteStat", back_populates="uuid")


class SiteStat(Base):
    __tablename__ = "site_statistics"

    id: int = Column(Integer, primary_key=True, index=True)
    uuid_id: str = Column(ForeignKey("uuids.id"))
    visit_date: datetime = Column(DateTime, default=datetime.now())
    endpoint: str = Column(String(100), default="/")

    uuid: Mapped["UUID"] = relationship("UUID", back_populates="sites")
