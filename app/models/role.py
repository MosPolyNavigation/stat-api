from .base import Base
from .role_right_goal import RoleRightGoal
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship, Mapped

class Role(Base):
    """
    Класс для хранения ролей.

    Этот класс представляет таблицу "roles" в базе данных.

    Атрибуты:
        id: Идентификатор роли.
        name: Название роли.
        rights_goals: связь с таблицей RoleRightGoal
    """

    __tablename__ = "roles"

    id: int = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name: str = Column(
        String(50),
        unique=True,
        nullable=False
    )

    # ссылка на связующую таблицу РольПравоЦель для извлечения всех прав на все цели по роли
    rights_goals: Mapped[list["RoleRightGoal"]] = relationship()