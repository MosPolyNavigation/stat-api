from __future__ import annotations
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship
from .base import Base


class Goal(Base):
    """Сущность цели, на которую распространяются права."""

    __tablename__ = "goals"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)

    role_right_goals: Mapped[list["RoleRightGoal"]] = relationship(
        "RoleRightGoal",
        back_populates="goal",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Goal(id={self.id!r}, name={self.name!r})"
