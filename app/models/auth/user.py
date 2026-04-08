from collections import defaultdict
from sqlalchemy import Boolean, Column, Integer, String, Select, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship, joinedload
from app.models.auth.role_right_goal import RoleRightGoal
from app.models.auth.user_role import UserRole
from app.models.base import Base
from datetime import datetime


class User(Base):
    """Сущность пользователя приложения."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    login: str = Column(String(255), nullable=False, unique=True)
    hash: str = Column(String(255), nullable=False)
    token: str | None = Column(String(255), nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    fio: str | None = Column(String(255), nullable=True)
    registration_date: datetime = Column(DateTime(), default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
    token_expired_at: datetime | None = Column(DateTime(), nullable=True)

    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, login={self.login!r}, is_active={self.is_active!r})"
        )
