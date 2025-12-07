"""Проверка прав доступа для ручек API."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.auth_utils import get_current_active_user
from app.models import Goal, User


def require_rights(goal_name: str, *rights: str):
    """
    Возвращает зависимость FastAPI, которая проверяет наличие прав у пользователя.

    Пример: `Depends(require_rights("review", "edit", "delete"))`
    выбросит 401/403, если у пользователя нет хотя бы одного из перечисленных прав
    для указанной цели.
    """

    async def check_rights(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: AsyncSession = Depends(get_db),
    ):
        goal = (await db.execute(Select(Goal).filter(Goal.name == goal_name))).scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=404, detail=f"Цель '{goal_name}' не найдена")

        user_rights_by_goal = await current_user.get_rights(db)
        await db.close()

        user_rights = user_rights_by_goal.get(goal.name)
        if user_rights is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"У пользователя нет прав для цели '{goal_name}'",
            )

        missing_rights = [r for r in rights if r not in set(user_rights)]
        if missing_rights:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    f"Недостаточно прав ({', '.join(missing_rights)}) "
                    f"для цели '{goal_name}'"
                ),
            )

        return True

    return check_rights
