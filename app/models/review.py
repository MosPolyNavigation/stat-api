from sqlalchemy import ForeignKey, Text, DateTime, text as text_
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Column, Integer, String
from datetime import datetime
from typing import Optional
from app.models.base import Base
from app.models.stat.user_id import UserId
from app.models.problem import Problem


class Review(Base):
    """
    Класс для отзыва.

    Этот класс представляет таблицу "reviews" в базе данных.

    Attributes:
        id: Идентификатор выбранной аудитории.
        user_id: Идентификатор пользователя.
        text: Отзыв пользователя.
        problem_id: Вид проблемы, с которой столкнулся пользователь.
        image_name: Id изображения в директории статических объектов.
        user: Связь с таблицей "user_ids".
        problem: Связь с таблицей "problem".
    """
    __tablename__ = "reviews"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    user_id: str = Column(
        ForeignKey("user_ids.user_id"),
        nullable=False
    )
    text: str = Column(
        Text,
        nullable=False
    )
    problem_id: str = Column(
        ForeignKey("problems.id"),
        nullable=False
    )
    # FK на статус
    review_status_id: int = Column(
        ForeignKey("review_statuses.id"),
        nullable=False,
        server_default=text_("1"),  # по умолчанию бэклог
    )
    image_name: Optional[str] = Column(
        String(255),
        nullable=True
    )
    creation_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    user: Mapped["UserId"] = relationship()
    problem: Mapped["Problem"] = relationship()

    # relation на статус
    review_status: Mapped["ReviewStatus"] = relationship(
        "ReviewStatus",
        back_populates="reviews",
    )