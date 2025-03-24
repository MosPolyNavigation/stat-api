from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from typing import Optional
from .base import Base
from .user_id import UserId
from .problem import Problem


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

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    text: str = Column(Text, nullable=False)
    problem_id: str = Column(ForeignKey("problems.id"), nullable=False)
    image_name: Optional[str] = Column(String(255), nullable=True)
    creation_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)

    user: Mapped["UserId"] = relationship()
    problem: Mapped["Problem"] = relationship()
