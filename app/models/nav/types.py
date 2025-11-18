from app.models.base import Base
from sqlalchemy import Column, String, Integer


class Type(Base):
    __tablename__ = "types"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False, unique=True)
