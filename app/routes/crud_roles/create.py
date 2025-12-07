"""Создание ролей и привязка прав."""

import json
from typing import Union

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.auth_utils import get_current_user
from app.helpers.permissions import require_rights
from app.models.auth.goal import Goal
from app.models.auth.right import Right
from app.models.auth.role import Role
from app.models.auth.role_right_goal import RoleRightGoal
from app.models.auth.user import User
from app.schemas.role import RoleOut


async def fill_role_right_goal(db: AsyncSession, rights_by_goals: dict[str, list[str]]) -> list[RoleRightGoal]:
    """Преобразует словарь прав по целям в список моделей RoleRightGoal."""
    role_right_goal: list[RoleRightGoal] = []
    for goal_name, rights in rights_by_goals.items():
        goal_id: Union[int, None] = (await db.execute(Select(Goal.id).filter_by(name=goal_name))).scalar_one_or_none()
        if not goal_id:
            raise HTTPException(400, f"Цель '{goal_name}' не найдена")

        for r in rights:
            right_id: Union[int, None] = (await db.execute(Select(Right.id).filter_by(name=r))).scalar_one_or_none()
            if not right_id:
                raise HTTPException(400, f"Право '{r}' не найдено")

            role_right_goal.append(RoleRightGoal(goal_id=goal_id, right_id=right_id))
    return role_right_goal


def register_endpoint(router: APIRouter):
    """Регистрирует POST создания роли."""

    @router.post(
        "",
        description="Создает новую роль и список прав.",
        response_model=RoleOut,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_rights("roles", "create"))],
    )
    async def create_role(
        name: str = Form(...),
        # JSON-строка с правами по целям, пример: {"users":["view","edit"],"roles":["view"]}
        rights_by_goals: str = Form(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        """Создает роль после проверки прав и корректности прав доступа."""
        try:
            rights_by_goals = json.loads(rights_by_goals)
        except json.JSONDecodeError:
            raise HTTPException(400, "rights_by_goals должен быть валидным JSON")

        existing: Union[Role, None] = (await db.execute(Select(Role).filter(Role.name == name))).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Роль с таким именем уже существует",
            )

        user_rights = await current_user.get_rights(db)

        for goal_name, rights in rights_by_goals.items():
            if goal_name not in user_rights:
                raise HTTPException(
                    status_code=403,
                    detail=f"Нет доступа к цели '{goal_name}'",
                )
            for r in rights:
                if r not in user_rights[goal_name]:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Нет права '{r}' для цели '{goal_name}'",
                    )

        new_role = Role(name=name, role_right_goals=await fill_role_right_goal(db, rights_by_goals))
        db.add(new_role)
        await db.commit()
        await db.refresh(new_role)

        return RoleOut(id=new_role.id, name=new_role.name, rights_by_goals=rights_by_goals)
