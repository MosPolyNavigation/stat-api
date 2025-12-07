"""Чтение ролей и их прав."""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.role import Role
from app.models.auth.role_right_goal import RoleRightGoal
from app.routes.get.generate_resp import generate_resp
from app.schemas.role import RoleOut


def build_rights_by_goals(role: Role) -> dict:
    """Строит словарь прав по целям из связей роли."""
    result = {}
    for rrg in role.role_right_goals:
        result.setdefault(rrg.goal.name, []).append(rrg.right.name)
    return result


def register_endpoint(router: APIRouter):
    """Регистрирует GET-ручки для получения ролей."""

    @router.get(
        "",
        description="Возвращает список ролей постранично.",
        response_model=Page[RoleOut],
        dependencies=[Depends(require_rights("roles", "view"))],
        responses=generate_resp(Page[RoleOut]),
    )
    async def read_roles(db: AsyncSession = Depends(get_db)):
        """Возвращает пагинированный список ролей."""
        roles_query = Select(Role).options(
            joinedload(Role.role_right_goals).joinedload(RoleRightGoal.goal),
            joinedload(Role.role_right_goals).joinedload(RoleRightGoal.right),
        )

        return await apaginate(db, roles_query)

    @router.get(
        "/{role_id}",
        description="Возвращает роль по идентификатору.",
        response_model=RoleOut,
        dependencies=[Depends(require_rights("roles", "view"))],
    )
    async def read_role(
        role_id: int,
        db: AsyncSession = Depends(get_db),
    ):
        """Возвращает роль и её права или 404, если не найдена."""
        role: Union[Role, None] = (
            (
                await db.execute(
                    Select(Role)
                    .options(
                        joinedload(Role.role_right_goals).joinedload(RoleRightGoal.goal),
                        joinedload(Role.role_right_goals).joinedload(RoleRightGoal.right),
                    )
                    .filter(Role.id == role_id)
                )
            ).scalar_one_or_none()
        )

        if not role:
            raise HTTPException(404, "Роль не найдена")

        return RoleOut(id=role.id, name=role.name, rights_by_goals=build_rights_by_goals(role))
