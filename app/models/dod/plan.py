from typing import Union
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base
from app.models.dod.corpus import DodCorpus
from app.models.dod.floor import DodFloor
from app.models.dod.static import DodStatic


class DodPlan(Base):
    __tablename__ = "dod_plans"

    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(20), nullable=False, unique=True)
    cor_id: int = Column(ForeignKey("dod_corpuses.id"), nullable=False)
    floor_id: int = Column(ForeignKey("dod_floors.id"), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    entrances: str = Column(Text, nullable=False)
    graph: str = Column(Text, nullable=False)
    svg_id: Mapped[Union[int, None]] = Column(ForeignKey("dod_statics.id"), nullable=True)
    nearest_entrance: Union[str, None] = Column(String(50), nullable=True)
    nearest_man_wc: Union[str, None] = Column(String(50), nullable=True)
    nearest_woman_wc: Union[str, None] = Column(String(50), nullable=True)
    nearest_shared_wc: Union[str, None] = Column(String(50), nullable=True)

    floor: Mapped["DodFloor"] = relationship()
    corpus: Mapped["DodCorpus"] = relationship()
    svg: Mapped[Union["DodStatic", None]] = relationship()


