from sqlalchemy import Column, Integer, String
from app.models.base import Base


class DodType(Base):
    __tablename__ = "dod_types"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False, unique=True)


