from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, false, ForeignKey, DateTime, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base


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


class RoleRightGoal(Base):
    """Связь роли с правом и целью."""

    __tablename__ = "role_right_goals"

    role_id: int = Column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    right_id: int = Column(
        ForeignKey("rights.id", ondelete="CASCADE"),
        primary_key=True,
    )
    goal_id: int = Column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    can_grant: bool = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    role: Mapped["Role"] = relationship("Role", back_populates="role_right_goals")
    right: Mapped["Right"] = relationship("Right", back_populates="role_right_goals")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="role_right_goals")

    def __repr__(self) -> str:
        return (
            "RoleRightGoal("
            f"role_id={self.role_id!r}, right_id={self.right_id!r},"
            f"goal_id={self.goal_id!r}, can_grant={self.can_grant!r}"
            ")"
        )


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


class UserRole(Base):
    """Связь пользователя с ролью."""

    __tablename__ = "user_roles"

    user_id: int = Column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: int = Column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    def __repr__(self) -> str:
        return (
            "UserRole("
            f"user_id={self.user_id!r}, role_id={self.role_id!r}"
            ")"
        )


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

    user_logs: Mapped[list["UserLog"]] = relationship(
        "UserLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, login={self.login!r}, is_active={self.is_active!r})"
        )


class UserLog(Base):
    __tablename__ = "user_logs"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    text: str = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_logs")


class RefreshToken(Base):
    """Активная refresh-сессия пользователя."""

    __tablename__ = "refresh_tokens"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jti: str = Column(String(255), nullable=False, unique=True)
    exp_date: datetime = Column(DateTime(), nullable=False)
    browser: str | None = Column(String(255), nullable=True)
    user_ip: str | None = Column(String(255), nullable=True)
    revoked: bool = Column(Boolean, default=False, nullable=False)
    created_at: datetime = Column(DateTime(), default=datetime.now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"RefreshToken(id={self.id!r}, user_id={self.user_id!r}, revoked={self.revoked!r})"

