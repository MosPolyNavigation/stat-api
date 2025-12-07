"""Связка роль-право-цель."""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class RoleRightGoal(Base):
    """Многие-ко-многим между ролями, правами и целями."""

    __tablename__ = "role_right_goals"

    role_id: int = Column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    right_id: int = Column(ForeignKey("rights.id", ondelete="CASCADE"), primary_key=True)
    goal_id: int = Column(ForeignKey("goals.id", ondelete="CASCADE"), primary_key=True)

    role: Mapped["Role"] = relationship("Role", back_populates="role_right_goals")
    right: Mapped["Right"] = relationship("Right", back_populates="role_right_goals")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="role_right_goals")

    def __repr__(self) -> str:  # pragma: no cover - служебный вывод
        return f"RoleRightGoal(role_id={self.role_id!r}, right_id={self.right_id!r}, goal_id={self.goal_id!r})"
