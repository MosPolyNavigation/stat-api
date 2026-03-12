from typing import List, Union
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base
from app.models.dod.plan import DodPlan
from app.models.dod.types import DodType


class DodAuditory(Base):
    __tablename__ = "dod_auditories"

    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(50), nullable=False)
    type_id: int = Column(ForeignKey("dod_types.id"), nullable=False)
    ready: bool = Column(Boolean, nullable=False, default=False)
    plan_id: int = Column(ForeignKey("dod_plans.id"), nullable=False)
    name: str = Column(String(20), nullable=False)
    text_from_sign: Union[str, None] = Column(String(200), nullable=True)
    additional_info: Union[str, None] = Column(String(200), nullable=True)
    comments: Union[str, None] = Column(String(200), nullable=True)
    link: Union[str, None] = Column(String(255), nullable=True)

    typ: Mapped["DodType"] = relationship()
    plans: Mapped["DodPlan"] = relationship()
    photos: Mapped[List["DodAudPhoto"]] = relationship(back_populates="auditory")


