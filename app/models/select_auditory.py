from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from .base import Base


class SelectAuditory(Base):
    __tablename__ = "selected_auditories"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    auditory_id: str = Column(ForeignKey("auditories.id"), nullable=False)
    success: bool = Column(Boolean, default=False, nullable=False)

    user: Mapped["UserId"] = relationship("UserId", back_populates="selected")
    auditory: Mapped["Auditory"] = relationship("Auditory", back_populates="selected")
