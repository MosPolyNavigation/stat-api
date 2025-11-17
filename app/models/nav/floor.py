from sqlalchemy import Column, Integer
from app.models.base import Base


class Floor(Base):
    __tablename__ = "floors"
    id: int = Column(Integer, primary_key=True)
    name: int = Column(Integer, nullable=False)
