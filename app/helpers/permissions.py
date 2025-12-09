"""Функции для проверки прав доступа в зависимости от цели (goal/right)."""

from sqlalchemy import Select
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, Goal
from app.helpers.auth_utils import get_current_active_user


def require_rights(goal_name: str, *rights: str):
    """
    Формирует зависимость FastAPI, проверяющую набор прав у текущего пользователя.

    Пример использования: `require_rights("review", "edit", "delete")`.

    Args:
        goal_name: Имя цели (goal), например review или nav_data.
        *rights: Список прав, которые необходимо подтвердить.

    Returns:
        Callable: Зависимость FastAPI, выбрасывающая HTTP 401/404 при отсутствии прав.
    """
    async def check_rights(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: AsyncSession = Depends(get_db),
    ):
        goal = (await db.execute(Select(Goal).filter(Goal.name == goal_name))).scalar_one()
        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f"Цель '{goal_name}' не найдена"
            )

        user_rights_by_goal = await current_user.get_rights(db)
        await db.close()
        user_rights = user_rights_by_goal[goal.name]

        user_rights_set = {r for r in user_rights}

        missing_rights = [r for r in rights if r not in user_rights_set]
        if missing_rights:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    f"У пользователя нет прав {', '.join(missing_rights)} "
                    f"для цели '{goal_name}'"
                ),
            )

        return True

    return check_rights
