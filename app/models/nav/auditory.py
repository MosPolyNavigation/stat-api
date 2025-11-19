from sqlalchemy.orm import Mapped, relationship
from typing import Union
from app.models.base import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.models.nav.plan import Plan
from app.models.nav.types import Type
from app.models.nav.static import Static


class Auditory(Base):
    __tablename__ = "auditories"
    id: int = Column(Integer, primary_key=True)
    id_sys: String = Column(String(50), nullable=False, unique=True)
    type_id: int = Column(ForeignKey("types.id"), nullable=False)
    ready: bool = Column(Boolean, nullable=False, default=False)
    plan_id: int = Column(ForeignKey("plans.id"), nullable=False)
    name: str = Column(String(20), nullable=False)
    text_from_sign: Union[str, None] = Column(String(200), nullable=True)
    additional_info: Union[str, None] = Column(String(200), nullable=True)
    comments: Union[str, None] = Column(String(200), nullable=True)
    link: Union[str, None] = Column(String(255), nullable=True)
    photo_id: Mapped[Union[int, None]] = Column(ForeignKey("statics.id"), nullable=True)

    typ: Mapped["Type"] = relationship()
    plans: Mapped["Plan"] = relationship()
    photo: Mapped[Union["Static", None]] = relationship()
