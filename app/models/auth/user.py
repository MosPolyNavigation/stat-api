from collections import defaultdict
from sqlalchemy import Boolean, Column, Integer, String, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship, joinedload
from app.models.auth.role_right_goal import RoleRightGoal
from app.models.auth.user_role import UserRole
from app.models.base import Base


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

    async def get_rights(self, db: AsyncSession) -> dict[str, list[str]]:
        role_right_goals = (
            (await db.execute(
                Select(RoleRightGoal)
                .join(UserRole, RoleRightGoal.role_id == UserRole.role_id)
                .filter(UserRole.user_id == self.id)
                .options(
                    joinedload(RoleRightGoal.right),
                    joinedload(RoleRightGoal.goal)
                )
            )).scalars().all()
        )

        # Группируем права по целям
        rights_by_goal = defaultdict(list)
        seen = set()

        for rrg in role_right_goals:
            goal_name = rrg.goal.name
            right_name = rrg.right.name
            key = (goal_name, right_name)
            if key not in seen:
                rights_by_goal[goal_name].append(right_name)
                seen.add(key)

        # Преобразуем defaultdict в обычный dict
        return dict(rights_by_goal)

    async def is_capable(self, db: AsyncSession, goal: str, right: str) -> bool:

        if not goal or not right:
            raise ValueError("goal and right must be provided for capability checks")
        if not self.is_active:
            raise PermissionError("Inactive user cannot execute actions")

        rights_by_goal = await self.get_rights(db)
        goal_rights = rights_by_goal.get(goal)
        if goal_rights is None:
            return False
        return right in goal_rights

