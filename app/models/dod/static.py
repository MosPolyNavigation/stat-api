from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.models.base import Base


class DodStatic(Base):
    __tablename__ = "dod_statics"

    id: int = Column(Integer, primary_key=True)
    ext: str = Column(String(6), nullable=False)
    path: str = Column(String(255), nullable=False)
    name: str = Column(String(50), nullable=False, unique=True)
    link: str = Column(String(255), nullable=False)
    creation_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )
    update_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )


