from sqlalchemy.orm import Mapped, relationship
from typing import Union
from app.models.base import Base
from sqlalchemy import Boolean, Integer, String, Text, Column, ForeignKey
from app.models.nav.corpus import Corpus
from app.models.nav.auditory import Auditory
from app.models.nav.floor import Floor
from app.models.nav.static import Static


class Plan(Base):
    __tablename__ = "plans"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(20), nullable=False)
    cor_id: int = Column(ForeignKey("corpuses.id"), nullable=False)
    floor_id: int = Column(ForeignKey("floors.id"), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    entrances: str = Column(Text, nullable=False)
    graph: str = Column(Text, nullable=False)
    svg_id: Union[int, None] = Column(ForeignKey("statics.id"), nullable=True)
    nearest_entrance_id: Union[int, None] = Column(ForeignKey("auditories.id"), nullable=True)
    nearest_man_wc_id: Union[int, None] = Column(ForeignKey("auditories.id"), nullable=True)
    nearest_woman_wc_id: Union[int, None] = Column(ForeignKey("auditories.id"), nullable=True)
    nearest_shared_wc_id: Union[int, None] = Column(ForeignKey("auditories.id"), nullable=True)

    floor: Mapped["Floor"] = relationship()
    corpus: Mapped["Corpus"] = relationship()
    svg: Union[Mapped["Static"], None] = relationship()
    nearest_entrance: Union[Mapped["Auditory"], None] = relationship(
        primaryjoin="Plan.nearest_entrance_id == Auditory.id")
    nearest_man_wc: Union[Mapped["Auditory"], None] = relationship(
        primaryjoin="Plan.nearest_man_wc_id == Auditory.id")
    nearest_woman_wc: Union[Mapped["Auditory"], None] = relationship(
        primaryjoin="Plan.nearest_woman_wc_id == Auditory.id")
    nearest_shared_wc: Union[Mapped["Auditory"], None] = relationship(
        primaryjoin="Plan.nearest_shared_wc_id == Auditory.id")
