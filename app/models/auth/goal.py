"""Цели доступа (группировка прав)."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class Goal(Base):
    """Цель, к которой привязаны права (например, users, roles и т.п.)."""

    __tablename__ = "goals"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)

    role_right_goals: Mapped[list["RoleRightGoal"]] = relationship(
        "RoleRightGoal",
        back_populates="goal",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - служебный вывод
        return f"Goal(id={self.id!r}, name={self.name!r})"
