from typing import Union
from sqlalchemy import String, Integer, Boolean, Text, Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base
from app.models.nav.location import Location


class Corpus(Base):
    __tablename__ = "corpuses"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(7), nullable=False, unique=True)
    loc_id: int = Column(ForeignKey("locations.id"), nullable=False)
    name: str = Column(String(20), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    stair_groups: Union[str, None] = Column(Text, nullable=True)
    comments: Union[str, None] = Column(String(100), nullable=True)

    locations: Mapped["Location"] = relationship()
