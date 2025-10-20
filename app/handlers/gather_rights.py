from collections import defaultdict

from sqlalchemy import Select
from sqlalchemy.orm import Session, joinedload
from app.models import UserRole, User, RoleRightGoal


def gather_rights_by_role(db: Session, current_user: User) -> dict[str, list[str]]:
    role_right_goals = (
        db.execute(
            Select(RoleRightGoal)
            .join(UserRole, RoleRightGoal.role_id == UserRole.role_id)
            .filter(UserRole.user_id == current_user.id)
            .options(
                joinedload(RoleRightGoal.right),
                joinedload(RoleRightGoal.goal)
            )
        ).scalars().all()
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
