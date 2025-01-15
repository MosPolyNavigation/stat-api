from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from .base import Base


class Plan(Base):
    """
    Класс для плана.

    Этот класс представляет таблицу "plans" в базе данных.

    Attributes:
        id: Идентификатор плана.
    """
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
