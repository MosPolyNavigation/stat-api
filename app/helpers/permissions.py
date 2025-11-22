from sqlalchemy import Select
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, Goal
from app.helpers.auth_utils import get_current_active_user


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
        goal = (await db.execute(Select(Goal).filter(Goal.name == goal_name))).scalar_one()
        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f"Цель (субъект) '{goal_name}' не найдена"
            )

        # Получаем роли пользователя
        user_rights_by_goal = await current_user.get_rights(db)
        await db.close()
        user_rights = user_rights_by_goal[goal.name]

        user_rights_set = {r for r in user_rights}

        # Проверяем наличие всех нужных прав
        missing_rights = [r for r in rights if r not in user_rights_set]
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
