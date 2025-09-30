from __future__ import annotations
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship
from .base import Base


class Right(Base):
    """Сущность права системы."""

    __tablename__ = "rights"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False, unique=True)

    role_right_goals: Mapped[list["RoleRightGoal"]] = relationship(
        "RoleRightGoal",
        back_populates="right",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Right(id={self.id!r}, name={self.name!r})"
