from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base
from app.models.dod.auditory import Auditory


class AudPhoto(Base):
    __tablename__ = "dod_aud_photo"

    id: int = Column(Integer, primary_key=True)
    aud_id: int = Column(ForeignKey("dod_auditories.id"), nullable=False)
    ext: str = Column(String(6), nullable=False)
    name: str = Column(String(50), nullable=False, unique=True)
    path: str = Column(String(255), nullable=False)
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

    auditory: Mapped["Auditory"] = relationship(Auditory, back_populates="photos")


