from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RoleRightGoal, Right, Goal, UserRole
from app.helpers.auth_utils import get_current_active_user, get_current_user


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
        db: Session = Depends(get_db),
    ):
        # Находим цель по имени
        goal = db.query(Goal).filter(Goal.name == goal_name).first()
        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f"Цель (субъект) '{goal_name}' не найдена"
            )

        # Получаем роли пользователя
        user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
        if not user_roles:
            raise HTTPException(
                status_code=401,
                detail="У пользователя нет назначенных ролей"
            )

        role_ids = [ur.role_id for ur in user_roles]

        # Получаем все права пользователя для этой цели
        user_rights = (
            db.query(Right.name)
            .join(RoleRightGoal, RoleRightGoal.right_id == Right.id)
            .filter(RoleRightGoal.goal_id == goal.id)
            .filter(RoleRightGoal.role_id.in_(role_ids))
            .all()
        )

        user_rights_set = {r.name for r in user_rights}

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
