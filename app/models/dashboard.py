from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base
from app.models.event import EventType


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
