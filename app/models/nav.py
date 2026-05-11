from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, relationship
from typing import Optional, List

from app.models import Base


class Location(Base):
    __tablename__ = "locations"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(2), unique=True, nullable=False)
    name: str = Column(String(25), nullable=False)
    short: str = Column(String(2), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    address: str = Column(String(255), nullable=False)
    metro: str = Column(String(255), nullable=False)
    crossings: Optional[str] = Column(Text, nullable=True)
    comments: Optional[str] = Column(String(255))


class Corpus(Base):
    __tablename__ = "corpuses"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(7), nullable=False, unique=True)
    loc_id: int = Column(ForeignKey("locations.id"), nullable=False)
    name: str = Column(String(20), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    stair_groups: Optional[str] = Column(Text, nullable=True)
    comments: Optional[str] = Column(String(100), nullable=True)

    locations: Mapped["Location"] = relationship("Location")


class Floor(Base):
    __tablename__ = "floors"
    id: int = Column(Integer, primary_key=True)
    name: int = Column(Integer, nullable=False, unique=True)


class Static(Base):
    __tablename__ = "statics"
    id: int = Column(Integer, primary_key=True)
    ext: str = Column(String(6), nullable=False)
    path: str = Column(String(255), nullable=False)
    name: str = Column(String(50), nullable=False, unique=True)
    link: str = Column(String(255), nullable=False)
    creation_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
    update_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )


class Plan(Base):
    __tablename__ = "plans"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(20), nullable=False, unique=True)
    cor_id: int = Column(ForeignKey("corpuses.id"), nullable=False)
    floor_id: int = Column(ForeignKey("floors.id"), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    entrances: str = Column(Text, nullable=False)
    graph: str = Column(Text, nullable=False)
    svg_id: Mapped[Optional[int]] = Column(ForeignKey("statics.id"), nullable=True)
    nearest_entrance: Optional[str] = Column(String(50), nullable=True)
    nearest_man_wc: Optional[str] = Column(String(50), nullable=True)
    nearest_woman_wc: Optional[str] = Column(String(50), nullable=True)
    nearest_shared_wc: Optional[str] = Column(String(50), nullable=True)

    floor: Mapped["Floor"] = relationship("Floor")
    corpus: Mapped["Corpus"] = relationship("Corpus")
    svg: Mapped[Optional["Static"]] = relationship("Static")


class Type(Base):
    __tablename__ = "types"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False, unique=True)


class Auditory(Base):
    __tablename__ = "auditories"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(50), nullable=False)
    type_id: int = Column(ForeignKey("types.id"), nullable=False)
    ready: bool = Column(Boolean, nullable=False, default=False)
    plan_id: int = Column(ForeignKey("plans.id"), nullable=False)
    name: str = Column(String(20), nullable=False)
    text_from_sign: Optional[str] = Column(String(200), nullable=True)
    additional_info: Optional[str] = Column(String(200), nullable=True)
    comments: Optional[str] = Column(String(200), nullable=True)
    link: Optional[str] = Column(String(255), nullable=True)

    typ: Mapped["Type"] = relationship("Type")
    plans: Mapped["Plan"] = relationship("Plan")
    photos: Mapped[List["AudPhoto"]] = relationship("AudPhoto", back_populates="auditory")


class AudPhoto(Base):
    __tablename__ = "aud_photo"

    id: int = Column(Integer, primary_key=True)
    aud_id: int = Column(ForeignKey("auditories.id"), nullable=False)
    ext: str = Column(String(6), nullable=False)
    name: str = Column(String(50), nullable=False, unique=True)
    path: str = Column(String(255), nullable=False)
    link: str = Column(String(255), nullable=False)
    creation_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )
    update_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    auditory: Mapped["Auditory"] = relationship("Auditory", back_populates="photos")
