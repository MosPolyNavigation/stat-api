from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base


class TgUser(Base):
    """
    Таблица для хранения пользователей телеграм-бота.

    Attributes:
        id: Внутренний идентификатор пользователя бота;
        tg_id: Telegram ID пользователя (int64).
    """
    __tablename__ = "tg_users"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    tg_id: int = Column(
        BigInteger,
        nullable=False,
        unique=True,
        index=True
    )

    events: Mapped[list["TgEvent"]] = relationship(
        "TgEvent",
        back_populates="tg_user"
    )


class TgEventType(Base):
    """
    Справочник типов событий телеграм-бота.

    Attributes:
        id: Идентификатор типа события;
        name: Название типа.
    """
    __tablename__ = "tg_event_types"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name: str = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    events: Mapped[list["TgEvent"]] = relationship(
        "TgEvent",
        back_populates="event_type"
    )


class TgEvent(Base):
    """
    Таблица событий телеграм-бота.

    Attributes:
        id: Идентификатор события;
        time: Время возникновения события;
        tg_user_id: Ссылка на пользователя (tg_users.id);
        event_type_id: Ссылка на тип события;
        is_dod: Признак, что событие относится к боту ДОД.
    """
    __tablename__ = "tg_events"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    time: datetime = Column(
        DateTime,
        nullable=False,
        index=True
    )
    tg_user_id: int = Column(
        "tg_id",
        ForeignKey("tg_users.id"),
        nullable=False,
        index=True
    )
    event_type_id: int = Column(
        Integer,
        ForeignKey("tg_event_types.id"),
        nullable=False,
        index=True
    )
    is_dod: bool = Column(
        Boolean,
        nullable=False
    )

    tg_user: Mapped["TgUser"] = relationship(
        "TgUser",
        back_populates="events"
    )
    event_type: Mapped["TgEventType"] = relationship(
        "TgEventType",
        back_populates="events"
    )
