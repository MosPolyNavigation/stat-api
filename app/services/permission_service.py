from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import RoleRightGoal, Role, UserRole
from app.constants import RIGHTS_BY_NAME, GOALS_BY_NAME


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._permissions_cache: dict[int, Set[Tuple[int, int]]] = {}

    async def get_user_permissions(self, user_id: int) -> set[tuple[int, int]]:
        if user_id in self._permissions_cache:
            return self._permissions_cache[user_id]
        
        stmt = (
            select(RoleRightGoal)
            .join(UserRole, UserRole.role_id == RoleRightGoal.role_id)
            .join(Role, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        rrgs: list[RoleRightGoal] = result.scalars().all()
        permissions = {(rrg.right_id, rrg.goal_id) for rrg in rrgs}
        self._permissions_cache[user_id] = permissions
        
        return permissions

    async def check_permission(self, user_id: int, resource: str, *actions: str) -> bool:
        perms: set[tuple[int, int]] = await self.get_user_permissions(user_id)

        action_ids = [RIGHTS_BY_NAME.get(action) for action in actions]
        resource_id = GOALS_BY_NAME.get(resource)

        required = {(action_id, resource_id) for action_id in action_ids}
        return required.issubset(perms)
