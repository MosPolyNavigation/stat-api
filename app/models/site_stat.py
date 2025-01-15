from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from .base import Base
from .user_id import UserId


class SiteStat(Base):
    """
    Класс для статистики посещений сайта.

    Этот класс представляет таблицу "site_statistics" в базе данных.

    Attributes:
        id: Идентификатор.
        user_id: Идентификатор пользователя.
        visit_date: Дата посещения.
        endpoint: Путь, посещенный пользователем.
        user: Связь с таблицей "user_ids".
    """
    __tablename__ = "site_statistics"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    endpoint: str = Column(String(100), nullable=True)

    user: Mapped["UserId"] = relationship()
