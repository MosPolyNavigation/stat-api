from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, relationship
from .base import Base
from .user_id import UserId
from typing import Optional
from enum import Enum as stdEnum

class Problem(str, stdEnum):
    PLAN = "plan"
    WORK = "work"
    WAY = "way"
    OTHER = "other"


class Review(Base):
    """
    Класс для отзыва.

    Этот класс представляет таблицу "reviews" в базе данных.

    Attributes:
        id: Идентификатор выбранной аудитории.
        user_id: Идентификатор пользователя.
        text: Отзыв пользователя.
        problem: Вид проблемы, с которой столкнулся пользователь.
        image_id: Id изображения в директории статических объектов.
        image_ext: Расширение файла.
        user: Связь с таблицей "user_ids".
    """
    __tablename__ = "reviews"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    text: str = Column(Text, nullable=False)
    problem: Problem = Column(Enum(Problem), nullable=False)
    image_id: Optional[str] = Column(String(255), nullable=True)
    image_ext: Optional[str] = Column(String(4), nullable=True)

    user: Mapped["UserId"] = relationship()
