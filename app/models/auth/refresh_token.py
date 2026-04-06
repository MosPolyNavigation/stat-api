from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base


class RefreshToken(Base):
    """Активная refresh-сессия пользователя."""

    __tablename__ = "refresh_tokens"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jti: str = Column(String(255), nullable=False, unique=True)
    exp_date: datetime = Column(DateTime(), nullable=False)
    browser: str | None = Column(String(255), nullable=True)
    user_ip: str | None = Column(String(255), nullable=True)
    revoked: bool = Column(Boolean, default=False, nullable=False)
    created_at: datetime = Column(DateTime(), default=datetime.now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return (f"RefreshToken(id={self.id!r}, user_id={self.user_id!r}, revoked={self.revoked!r})")