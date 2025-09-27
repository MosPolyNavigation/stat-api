from .base import Base
from sqlalchemy import Column, String, ForeignKey, Integer

class UserRole(Base):
    """
    Класс для для связи многие-ко-многим между пользователями и ролями.

    Этот класс представляет таблицу "users_roles" в базе данных.

    Атрибуты:
        user_id: Внешний ключ на пользователя.
        role_id: Внешний ключ на роль.
    """

    __tablename__ = "users_roles"

    user_id: str = Column(
        String(36),
        ForeignKey("users.id"),
        primary_key=True
    )
    role_id: int = Column(
        Integer,
        ForeignKey("roles.id"),
        primary_key=True
    )