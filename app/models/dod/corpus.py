from typing import Union
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base
from app.models.dod.location import DodLocation


class DodCorpus(Base):
    __tablename__ = "dod_corpuses"

    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(7), nullable=False, unique=True)
    loc_id: int = Column(ForeignKey("dod_locations.id"), nullable=False)
    name: str = Column(String(20), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    stair_groups: Union[str, None] = Column(Text, nullable=True)
    comments: Union[str, None] = Column(String(100), nullable=True)

    locations: Mapped["DodLocation"] = relationship()


