from __future__ import annotations
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base


class Role(Base):
    """Сущность роли пользователя."""

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

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"
