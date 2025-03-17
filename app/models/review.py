from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, relationship
from .base import Base
from .user_id import UserId
from typing import Optional
from enum import Enum as stdEnum

class Problem(str, stdEnum):
    PLAN = "Неточность на плане"
    WORK = "Работа приложения"
    WAY = "Неправильный маршрут"
    OTHER = "Другое"


class Review(Base):
    """
    Класс для выбранной аудитории.

    Этот класс представляет таблицу "reviews" в базе данных.

    Attributes:
        id: Идентификатор выбранной аудитории.
        user_id: Идентификатор пользователя.
        text: Отзыв пользователя.
        problem: Вид проблемы, с которой столкнулся пользователь.
        image_path: Путь до прикрепленного изображения.
        user: Связь с таблицей "user_ids".
    """
    __tablename__ = "reviews"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=True)
    text: str = Column(Text, nullable=False)
    problem: Problem = Column(Enum(Problem), nullable=False)
    image_path: Optional[str] = Column(String(255), nullable=True)

    user: Mapped[Optional["UserId"]] = relationship()
