from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
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


class ClientId(Base):
    __tablename__ = "client_ids"

    id: int = Column(Integer, primary_key=True)
    ident: str = Column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
    )
    creation_date: datetime = Column(DateTime, default=datetime.now, nullable=False)

    events: Mapped[list["Event"]] = relationship(
        "Event",
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
