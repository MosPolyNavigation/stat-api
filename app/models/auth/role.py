"""Роли пользователей и их связи с правами."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class Role(Base):
    """Роль пользователя, объединяющая права и цели."""

    __tablename__ = "roles"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)

    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    role_right_goals: Mapped[list["RoleRightGoal"]] = relationship(
        "RoleRightGoal",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    @property
    def rights_by_goals(self):
        """Словарь вида {goal: [rights]} для удобства сериализации."""
        result = {}
        for rrg in self.role_right_goals:
            result.setdefault(rrg.goal.name, []).append(rrg.right.name)
        return result

    def __repr__(self) -> str:  # pragma: no cover - служебный вывод
        return f"Role(id={self.id!r}, name={self.name!r})"
