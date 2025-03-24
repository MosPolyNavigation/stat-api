from sqlalchemy import Column, String
from .base import Base


class Problem(Base):
    """
    Класс для хранения проблемы.

    Этот класс представляет таблицу "problems" в базе данных.

    Attributes:
        id: Наименование проблемы.
    """
    __tablename__ = "problems"

    id: str = Column(String(5), primary_key=True, index=True)
