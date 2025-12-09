"""CRUD-эндпоинты просмотра ролей."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from typing import Union
from app.database import get_db
from app.helpers.permissions import require_rights
from app.routes.get.generate_resp import generate_resp
from app.models.auth.role import Role
from app.models.auth.role_right_goal import RoleRightGoal
from app.schemas.role import RoleOut


def build_rights_by_goals(role: Role) -> dict:
    """
    Преобразует связи RoleRightGoal в структуру {goal: [rights]}.

    Args:
        role: Роль с загруженными связями.

    Returns:
        dict: Права, сгруппированные по целям.
    """
    result = {}
    for rrg in role.role_right_goals:
        result.setdefault(rrg.goal.name, []).append(rrg.right.name)
    return result


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинты просмотра ролей (список и конкретная роль).

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленными обработчиками.
    """

    @router.get(
        "",
        description="Получение списка ролей",
        response_model=Page[RoleOut],
        dependencies=[Depends(require_rights("roles", "view"))],
        responses=generate_resp(Page[RoleOut])
    )
    async def read_roles(db: AsyncSession = Depends(get_db)):
        """
        Возвращает список ролей с пагинацией.

        Args:
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Page[RoleOut]: Страница ролей.
        """

        roles_query = Select(Role).options(
            joinedload(Role.role_right_goals)
            .joinedload(RoleRightGoal.goal),
            joinedload(Role.role_right_goals)
            .joinedload(RoleRightGoal.right),
        )

        return await apaginate(db, roles_query)

    @router.get(
        "/{role_id}",
        description="Получение конкретной роли",
        response_model=RoleOut,
        dependencies=[Depends(require_rights("roles", "view"))]
    )
    async def read_role(
            role_id: int,
            db: AsyncSession = Depends(get_db)
    ):
        """
        Возвращает конкретную роль с перечнем прав.

        Args:
            role_id: Идентификатор роли.
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            RoleOut: Найденная роль.
        """

        role: Union[Role, None] = (
            (await db.execute(
                Select(Role)
                .options(
                    joinedload(Role.role_right_goals)
                    .joinedload(RoleRightGoal.goal),
                    joinedload(Role.role_right_goals)
                    .joinedload(RoleRightGoal.right),
                )
                .filter(Role.id == role_id))
             ).scalar_one_or_none()
        )

        if not role:
            raise HTTPException(404, "Роль не найдена")

        return RoleOut(
            id=role.id,
            name=role.name,
            rights_by_goals=build_rights_by_goals(role)
        )

    return router
