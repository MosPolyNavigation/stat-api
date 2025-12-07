"""Связка пользователь-роль."""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base


class UserRole(Base):
    """Ассоциация many-to-many между пользователями и ролями."""

    __tablename__ = "user_roles"

    user_id: int = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: int = Column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    def __repr__(self) -> str:  # pragma: no cover - служебный вывод
        return f"UserRole(user_id={self.user_id!r}, role_id={self.role_id!r})"
