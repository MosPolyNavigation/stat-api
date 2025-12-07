"""Отдельное право внутри цели доступа."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class Right(Base):
    """Право, которое может входить в одну или несколько ролей."""

    __tablename__ = "rights"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)

    role_right_goals: Mapped[list["RoleRightGoal"]] = relationship(
        "RoleRightGoal",
        back_populates="right",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - служебный вывод
        return f"Right(id={self.id!r}, name={self.name!r})"
