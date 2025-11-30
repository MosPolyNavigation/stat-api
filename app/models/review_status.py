from __future__ import annotations

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class ReviewStatus(Base):
    """Статус отзыва."""

    __tablename__ = "review_statuses"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)

    # Все отзывы с данным статусом
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="review_status",
    )

