from .base import Base
from sqlalchemy import Column, String, Integer

class Goal(Base):
    """
    Класс для хранения целей.

    Этот класс представляет таблицу "goals" в базе данных.

    Атрибуты:
        id: Идентификатор цели.
        name: Название цели.
    """
    __tablename__ = "goals"

    id: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name: str = Column(
        String(100),
        unique=True,
        nullable=False
    )