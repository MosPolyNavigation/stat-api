from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base


class UserLog(Base):
    __tablename__ = "user_logs"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    text: str = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_logs")

