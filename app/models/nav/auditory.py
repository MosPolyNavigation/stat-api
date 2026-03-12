from sqlalchemy.orm import Mapped, relationship
from typing import List, Union
from app.models.base import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.models.nav.plan import Plan
from app.models.nav.types import Type


class Auditory(Base):
    __tablename__ = "auditories"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(50), nullable=False)
    type_id: int = Column(ForeignKey("types.id"), nullable=False)
    ready: bool = Column(Boolean, nullable=False, default=False)
    plan_id: int = Column(ForeignKey("plans.id"), nullable=False)
    name: str = Column(String(20), nullable=False)
    text_from_sign: Union[str, None] = Column(String(200), nullable=True)
    additional_info: Union[str, None] = Column(String(200), nullable=True)
    comments: Union[str, None] = Column(String(200), nullable=True)
    link: Union[str, None] = Column(String(255), nullable=True)

    typ: Mapped["Type"] = relationship(Type)
    plans: Mapped["Plan"] = relationship(Plan)
    photos: Mapped[List["AudPhoto"]] = relationship("app.models.nav.aud_photo.AudPhoto", back_populates="auditory")

