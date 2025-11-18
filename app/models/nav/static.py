from app.models.base import Base
from sqlalchemy import Column, Integer, String


class Static(Base):
    __tablename__ = "statics"
    id: int = Column(Integer, primary_key=True)
    ext: str = Column(String(6), nullable=False)
    path: str = Column(String(255), nullable=False)
    name: str = Column(String(50), nullable=False, unique=True)
