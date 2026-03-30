from typing import Annotated
from collections import defaultdict
from sqlalchemy import Select
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, Goal
from app.helpers.auth_utils import get_current_active_user
from app.services.permission_service import PermissionService
from app.constants import RIGHTS_BY_ID, GOALS_BY_ID


def group_rights_by_goals(rights_goals: set[tuple[int, int]]) -> dict[str, list[str]]:
    rights_by_goals = defaultdict(list)
    for right_id, goal_id in rights_goals:
        goal_name = GOALS_BY_ID.get(goal_id)
        right_name = RIGHTS_BY_ID.get(right_id)
        rights_by_goals[goal_name].append(right_name)
    return dict(rights_by_goals)


def require_rights(goal_name: str, *rights: str):
    """
    Проверяет, что текущий пользователь имеет указанные права для заданной цели (субъекта).
    Может принимать несколько прав, например: require_rights("review", "edit", "delete")

    Args:
        goal_name: имя цели (субъекта доступа)
        *rights: список прав, которые должны быть у пользователя
    """
    async def check_rights(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: AsyncSession = Depends(get_db),
    ):
        # Находим цель по имени
        service: PermissionService = PermissionService(db)
        rights_goals = await service.get_user_permissions(current_user.id)
        user_rights = group_rights_by_goals(rights_goals)[goal_name]

        # Проверяем наличие всех нужных прав
        missing_rights = [r for r in rights if r not in user_rights]
        if missing_rights:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    f"Пользователь не имеет права(а) "
                    f"{', '.join(missing_rights)} для цели '{goal_name}'"
                ),
            )

        # Всё хорошо, просто начинает запускаться эндпоинт
        return True

    return check_rights
