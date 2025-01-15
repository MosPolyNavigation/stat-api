from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from .auditory import Auditory
from .base import Base
from .user_id import UserId


class StartWay(Base):
    """
    Класс для отслеживания начатых маршрутов.

    Этот класс представляет таблицу "started_ways" в базе данных.

    Attributes:
        id: Идентификатор.
        user_id: Идентификатор пользователя.
        visit_date: Дата посещения.
        start_id: Идентификатор начала пути.
        end_id: Идентификатор конца пути.
        user: Связь с таблицей "user_ids".
        start: Связь с таблицей "auditories" для начала пути.
        end: Связь с таблицей "auditories" для конца пути.
    """
    __tablename__ = "started_ways"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: str = Column(ForeignKey("user_ids.user_id"), nullable=False)
    visit_date: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    start_id: Mapped[str] = mapped_column(ForeignKey("auditories.id"), nullable=False)
    end_id: Mapped[str] = mapped_column(ForeignKey("auditories.id"), nullable=False)

    user: Mapped["UserId"] = relationship()
    start: Mapped["Auditory"] = relationship("Auditory", foreign_keys=[start_id])
    end: Mapped["Auditory"] = relationship("Auditory", foreign_keys=[end_id])
