from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from graphql import GraphQLError

from app.models import RoleRightGoal, UserRole
from app.constants import RIGHTS_BY_NAME, GOALS_BY_NAME, GOALS_BY_ID, RIGHTS_BY_ID


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._permissions_cache: dict[int, tuple[set[tuple[int, int]], set[tuple[int, int]]]] = {}

    async def get_user_permissions(self, user_id: int) -> set[tuple[int, int]]:
        permissions, _ = await self._get_cached_permissions(user_id)
        return permissions

    async def check_permission(self, user_id: int, resource: str, *actions: str) -> bool:
        perms: set[tuple[int, int]] = await self.get_user_permissions(user_id)

        action_ids = [RIGHTS_BY_NAME.get(action) for action in actions]
        resource_id = GOALS_BY_NAME.get(resource)

        required = {(action_id, resource_id) for action_id in action_ids}
        return required.issubset(perms)

    async def _get_cached_permissions(
        self,
        user_id: int,
    ) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        if user_id in self._permissions_cache:
            return self._permissions_cache[user_id]

        stmt = (
            select(
                RoleRightGoal.right_id,
                RoleRightGoal.goal_id,
                func.max(RoleRightGoal.can_grant).label("can_grant"),
            )
            .join(UserRole, UserRole.role_id == RoleRightGoal.role_id)
            .where(UserRole.user_id == user_id)
            .group_by(RoleRightGoal.right_id, RoleRightGoal.goal_id)
        )
        result = await self.db.execute(stmt)

        permissions: set[tuple[int, int]] = set()
        grantable_permissions: set[tuple[int, int]] = set()

        for right_id, goal_id, can_grant in result.all():
            permission = (right_id, goal_id)
            permissions.add(permission)
            if can_grant:
                grantable_permissions.add(permission)

        self._permissions_cache[user_id] = (permissions, grantable_permissions)
        return self._permissions_cache[user_id]

    async def check_grant_permissions(
        self,
        user_id: int,
        permissions: list[tuple[int, int]],
    ) -> list[str]:
        """
        Возвращает пустой список при успехе, иначе список ошибок.
        Ошибка генерируется, если у пользователя нет права ИЛИ can_grant=False.
        """
        if not permissions:
            return []

        all_permissions, grantable_permissions = await self._get_cached_permissions(user_id)
        required_permissions = set(permissions)

        if required_permissions.issubset(grantable_permissions):
            return []

        errors: list[str] = []
        for right_id, goal_id in required_permissions:
            right_name = RIGHTS_BY_ID.get(right_id)
            goal_name = GOALS_BY_ID.get(goal_id)

            if right_name is None or goal_name is None:
                unknown = []
                if right_name is None:
                    unknown.append(f"right_id={right_id}")
                if goal_name is None:
                    unknown.append(f"goal_id={goal_id}")
                raise GraphQLError(f"Неизвестный идентификатор права/цели: {', '.join(unknown)}")

            permission = (right_id, goal_id)
            if permission not in all_permissions:
                errors.append(f"{right_name} -> {goal_name}")
                continue

            if permission not in grantable_permissions:
                errors.append(f"{right_name} -> {goal_name} (делегирование запрещено)")

        return errors