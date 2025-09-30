from __future__ import annotations
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped, relationship
from .base import Base


class User(Base):
    """Сущность пользователя приложения."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    login: str = Column(String(255), nullable=False, unique=True)
    hash: str = Column(String(255), nullable=False)
    token: str | None = Column(String(255), nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False)

    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, login={self.login!r}, is_active={self.is_active!r})"
        )
