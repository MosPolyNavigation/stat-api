from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text as text_
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class EventType(Base):
    __tablename__ = "event_types"

    id: int = Column(Integer, primary_key=True)
    code_name: str = Column(String(20), unique=True, nullable=False)
    description: str | None = Column(String(100), nullable=True)

    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="event_type",
    )
    allowed_payloads: Mapped[list["AllowedPayload"]] = relationship(
        "AllowedPayload",
        back_populates="event_type",
    )
    dashboards: Mapped[list["Dashboard"]] = relationship(
        "Dashboard",
        back_populates="event_type",
    )


class ClientId(Base):
    __tablename__ = "client_ids"

    id: int = Column(Integer, primary_key=True)
    ident: str = Column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
    )
    creation_date: datetime = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="client",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="client",
    )


class Event(Base):
    __tablename__ = "events"

    id: int = Column(Integer, primary_key=True)
    client_id: int = Column(
        ForeignKey("client_ids.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    event_type_id: int = Column(
        ForeignKey("event_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    trigger_time: datetime = Column(DateTime, nullable=False)

    client: Mapped["ClientId"] = relationship(
        "ClientId",
        back_populates="events",
    )
    event_type: Mapped["EventType"] = relationship(
        "EventType",
        back_populates="events",
    )
    payloads: Mapped[list["Payload"]] = relationship(
        "Payload",
        back_populates="event",
    )


class ValueType(Base):
    __tablename__ = "value_types"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(20), nullable=False)
    description: str | None = Column(String(100), nullable=True)

    payload_types: Mapped[list["PayloadType"]] = relationship(
        "PayloadType",
        back_populates="value_type",
    )


class PayloadType(Base):
    __tablename__ = "payload_types"

    id: int = Column(Integer, primary_key=True)
    code_name: str = Column(String(20), unique=True, nullable=False)
    description: str | None = Column(String(100), nullable=True)
    value_type_id: int = Column(
        ForeignKey("value_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    value_type: Mapped["ValueType"] = relationship(
        "ValueType",
        back_populates="payload_types",
    )
    payloads: Mapped[list["Payload"]] = relationship(
        "Payload",
        back_populates="payload_type",
    )
    allowed_payloads: Mapped[list["AllowedPayload"]] = relationship(
        "AllowedPayload",
        back_populates="payload_type",
    )


class Payload(Base):
    __tablename__ = "payloads"

    id: int = Column(Integer, primary_key=True)
    event_id: int = Column(
        ForeignKey("events.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    type_id: int = Column(
        ForeignKey("payload_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    value: str = Column(String(50), nullable=False)

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="payloads",
    )
    payload_type: Mapped["PayloadType"] = relationship(
        "PayloadType",
        back_populates="payloads",
    )


class AllowedPayload(Base):
    __tablename__ = "allowed_payloads"

    event_type_id: int = Column(
        ForeignKey("event_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    payload_type_id: int = Column(
        ForeignKey("payload_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    event_type: Mapped["EventType"] = relationship(
        "EventType",
        back_populates="allowed_payloads",
    )
    payload_type: Mapped["PayloadType"] = relationship(
        "PayloadType",
        back_populates="allowed_payloads",
    )


class DashboardType(Base):
    __tablename__ = "dashboard_types"

    id: int = Column(Integer, primary_key=True)
    code_name: str = Column(String(20), unique=True, nullable=False)
    description: str | None = Column(String(100), nullable=True)

    dashboards: Mapped[list["Dashboard"]] = relationship(
        "Dashboard",
        back_populates="dashboard_type",
    )


class Dashboard(Base):
    __tablename__ = "dashboards"

    id: int = Column(Integer, primary_key=True)
    display_order: int = Column(Integer, nullable=False)
    event_type_id: int = Column(
        ForeignKey("event_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    dashboard_type_id: int = Column(
        ForeignKey("dashboard_types.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    title_text: str = Column(String(100), nullable=False)

    event_type: Mapped["EventType"] = relationship(
        "EventType",
        back_populates="dashboards",
    )
    dashboard_type: Mapped["DashboardType"] = relationship(
        "DashboardType",
        back_populates="dashboards",
    )


class Problem(Base):
    """
    Класс для хранения проблемы.

    Этот класс представляет таблицу "problems" в базе данных.

    Attributes:
        id: Наименование проблемы.
    """
    __tablename__ = "problems"

    id: str = Column(String(5), primary_key=True, index=True)


class ReviewStatus(Base):
    """Статус отзыва."""

    __tablename__ = "review_statuses"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)

    # Все отзывы с данным статусом
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="review_status",
    )


class Review(Base):
    """
    Класс для отзыва.

    Этот класс представляет таблицу "reviews" в базе данных.

    Attributes:
        id: Идентификатор отзыва.
        client_id: Идентификатор клиента из таблицы "client_ids".
        text: Отзыв пользователя.
        problem_id: Вид проблемы, с которой столкнулся пользователь.
        image_name: Id изображения в директории статических объектов.
        client: Связь с таблицей "client_ids".
        problem: Связь с таблицей "problem".
    """
    __tablename__ = "reviews"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    client_id: int = Column(
        ForeignKey("client_ids.id"),
        nullable=False
    )
    text: str = Column(
        Text,
        nullable=False
    )
    problem_id: str = Column(
        ForeignKey("problems.id"),
        nullable=False
    )
    # FK на статус
    review_status_id: int = Column(
        ForeignKey("review_statuses.id"),
        nullable=False,
        server_default=text_("1"),  # по умолчанию бэклог
    )
    image_name: Optional[str] = Column(
        String(255),
        nullable=True
    )
    creation_date: datetime = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    client: Mapped["ClientId"] = relationship(
        "ClientId",
        back_populates="reviews",
    )
    problem: Mapped["Problem"] = relationship()

    # relation на статус
    review_status: Mapped["ReviewStatus"] = relationship(
        "ReviewStatus",
        back_populates="reviews",
    )
