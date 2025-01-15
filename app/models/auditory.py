from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from .base import Base


class Auditory(Base):
    """
    Класс для аудитории.

    Этот класс представляет таблицу "auditories" в базе данных.

    Attributes:
        id: Идентификатор аудитории.
    """
    __tablename__ = "auditories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
