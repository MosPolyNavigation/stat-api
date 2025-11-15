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

    # Строит словарь прав роли в формате: { "goal_name": ["right1", "right2", ...] }
    @property
    def rights_by_goals(self):
        result = {}
        for rrg in self.role_right_goals:
            result.setdefault(rrg.goal.name, []).append(rrg.right.name)
        return result

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"
