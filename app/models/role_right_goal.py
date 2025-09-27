from .base import Base
from sqlalchemy import Column, ForeignKey, Integer

class RoleRightGoal(Base):
    """
    Класс для связи многие-ко-многим Роль Право Цель.

    Этот класс представляет таблицу "users_rights_roles" в базе данных.

    Атрибуты:
        role_id: Внешний ключ на роль.
        right_id: Внешний ключ на право.
        goal_id: Внешний ключ на цель.
    """

    __tablename__ = "users_rights_roles"

    role_id: int = Column(
        Integer,
        ForeignKey("roles.id"),
        primary_key=True
    )
    right_id: int = Column(
        Integer,
        ForeignKey("rights.id"),
        primary_key=True
    )
    goal_id: int = Column(
        Integer,
        ForeignKey("goals.id"),
        primary_key=True
    )