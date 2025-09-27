from .base import Base
from sqlalchemy import Column, String, Integer

class Right(Base):
    """
    Класс для хранения прав.

    Этот класс представляет таблицу "rights" в базе данных.

    Атрибуты:
        id: Идентификатор права.
        name: Название права.
    """

    __tablename__ = "rights"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name: str = Column(
        String(100),
        unique=True,
        nullable=False
    )