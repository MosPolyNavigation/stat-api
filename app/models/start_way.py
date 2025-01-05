from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from .base import Base


class StartWay(Base):
    __tablename__ = "started_ways"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    start_id: Mapped[str] = mapped_column(ForeignKey("auditories.id"), nullable=False)
    end_id: Mapped[str] = mapped_column(ForeignKey("auditories.id"), nullable=False)

    user: Mapped["UserId"] = relationship("UserId", back_populates="started_ways")
    start: Mapped["Auditory"] = relationship("Auditory", foreign_keys=[start_id])
    end: Mapped["Auditory"] = relationship("Auditory", foreign_keys=[end_id])
