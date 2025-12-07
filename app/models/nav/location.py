from typing import Union
from app.models.base import Base
from sqlalchemy import Integer, String, Text, Column, Boolean


class Location(Base):
    __tablename__ = "locations"
    id: int = Column(Integer, primary_key=True)
    id_sys: str = Column(String(2), unique=True, nullable=False)
    name: str = Column(String(25), nullable=False)
    short: str = Column(String(2), nullable=False)
    ready: bool = Column(Boolean, nullable=False)
    address: str = Column(String(100), nullable=False)
    metro: str = Column(String(100), nullable=False)
    crossings: Union[str, None] = Column(Text, nullable=True)
    comments: Union[str, None] = Column(String(100))
