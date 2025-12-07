from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
# from .auditory import Auditory
from app.models.base import Base
from app.models.stat.user_id import UserId


class SelectAuditory(Base):
    """
    Класс для выбранной аудитории.

    Этот класс представляет таблицу "selected_auditories" в базе данных.

    Attributes:
        id: Идентификатор выбранной аудитории.
        user_id: Идентификатор пользователя.
        visit_date: Дата посещения.
        auditory_id: Идентификатор аудитории.
        success: Успешность выбора аудитории.
        user: Связь с таблицей "user_ids".
        auditory: Связь с таблицей "auditories".
    """
    __tablename__ = "selected_auditories"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    user_id: Mapped[str] = Column(
        ForeignKey("user_ids.user_id"),
        nullable=False
    )
    visit_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
    auditory_id: Mapped[str] = Column(
        # ForeignKey("auditories.id"),
        String,
        nullable=False
    )
    success: bool = Column(
        Boolean,
        default=False,
        nullable=False
    )

    user: Mapped["UserId"] = relationship()
    # auditory: Mapped["Auditory"] = relationship()
