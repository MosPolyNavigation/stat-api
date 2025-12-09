"""CRUD-эндпоинт для безопасного обновления ролей."""

from typing import Union
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import Select, Delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.auth.role import Role
from app.models.auth.role_right_goal import RoleRightGoal
from app.models.auth.goal import Goal
from app.models.auth.right import Right
from app.models.auth.user import User
from app.helpers.auth_utils import get_current_user_with_loaded_fields
from app.helpers.permissions import require_rights
from app.schemas.role import RoleOut
import json


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт частичного обновления роли.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным обработчиком.
    """

    @router.patch(
        "/{role_id}",
        description="Безопасное обновление роли",
        dependencies=[Depends(require_rights("roles", "edit"))]
    )
    async def update_role(
            role_id: int,
            name: str | None = Form(None),
            rights_by_goals: str | None = Form(None),
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(get_current_user_with_loaded_fields)
    ):
        """
        Обновляет имя роли и/или набор прав с проверкой полномочий.

        Args:
            role_id: Идентификатор роли.
            name: Новое имя роли.
            rights_by_goals: JSON-строка с правами вида {"goal": ["right"]}.
            db: Асинхронная сессия SQLAlchemy.
            current_user: Пользователь, выполняющий операцию.

        Returns:
            RoleOut: Обновленная роль.
        """
        if rights_by_goals:
            try:
                rights_by_goals = json.loads(rights_by_goals)
            except json.JSONDecodeError:
                raise HTTPException(
                    400,
                    detail="rights_by_goals должен быть валидным JSON"
                )

        role: Union[Role, None] = (await db.execute(Select(Role).filter(Role.id == role_id))).scalar_one_or_none()
        if not role:
            raise HTTPException(404, "Роль не найдена")

        user_role_ids = {ur.role_id for ur in current_user.user_roles}
        if role.id in user_role_ids:
            raise HTTPException(
                status_code=403,
                detail="Нельзя изменять роли, которыми вы обладаете"
            )

        if name:
            exists: Union[Role, None] = (await db.execute(
                Select(Role).filter(Role.name == name, Role.id != role.id))).scalar_one_or_none()
            if exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Роль с именем '{name}' уже существует"
                )
            role.name = name

        user_rights = await current_user.get_rights(db)

        if rights_by_goals is not None:

            for goal_name, rights_list in rights_by_goals.items():
                if goal_name not in user_rights:
                    raise HTTPException(
                        status_code=403,
                        detail=f"У вас нет прав на цель '{goal_name}'"
                    )

                for right_name in rights_list:
                    if right_name not in user_rights[goal_name]:
                        raise HTTPException(
                            status_code=403,
                            detail=f"У вас нет права '{right_name}' на цель '{goal_name}'"
                        )

                    right_obj: Union[Right, None] = (await db.execute(
                        Select(Right).filter_by(name=right_name))).scalar_one_or_none()
                    if not right_obj:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Право '{right_name}' не существует в системе"
                        )

                goal_obj = (await db.execute(Select(Goal).filter_by(name=goal_name))).scalar_one_or_none()
                if not goal_obj:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Цель '{goal_name}' не существует в системе"
                    )

            await db.execute(Delete(RoleRightGoal).filter_by(role_id=role_id))

            for goal_name, rights_list in rights_by_goals.items():
                goal_obj = (await db.execute(Select(Goal).filter_by(name=goal_name))).scalar_one()

                for right_name in rights_list:
                    right_obj = (await db.execute(Select(Right).filter_by(name=right_name))).scalar_one()

                    db.add(RoleRightGoal(
                        role_id=role.id,
                        goal_id=goal_obj.id,
                        right_id=right_obj.id
                    ))

        await db.commit()
        await db.refresh(role)

        rights_final = rights_by_goals if rights_by_goals else {}

        return RoleOut(
            id=role.id,
            name=role.name,
            rights_by_goals=rights_final
        )

    return router
