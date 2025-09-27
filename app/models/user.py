from .base import Base
from .user_role import UserRole
from sqlalchemy import Column, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship, Mapped

class User(Base):
    """
    Класс для хранения пользователей.

    Этот класс представляет таблицу "users" в базе данных.

    Атрибуты:
        id: id пользователя.
        login: Логин пользователя.
        passowrd_hash: хэш пользователя.
        token: токен пользователя.
        is_active: активное/неактивное состояние пользователя.
        roles: связь с таблицей UserRole.
    """

    __tablename__ = "users"

    id: str = Column(
        String(36),
        ForeignKey("user_ids.user_id"),
        primary_key=True
    )
    login: str = Column(
        String(50),
        unique=True,
        nullable=False
    )
    password_hash: str = Column(
        String(256),
        nullable=False
    )
    token: str = Column(
        String(256),
        nullable=True
    )
    is_active: bool = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # ссылка для извлечения всех ролей пользователя
    roles: Mapped[list["UserRole"]] = relationship()


