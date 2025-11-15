from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth.role import Role
from app.models.auth.role_right_goal import RoleRightGoal
from app.models.auth.goal import Goal
from app.models.auth.right import Right
from app.models.auth.user import User
from app.helpers.auth_utils import get_current_user
from app.helpers.permissions import require_rights
from app.schemas.role import RoleOut
import json


def register_endpoint(router: APIRouter):
    "Эндпоинт для изменения данных роли"

    @router.patch(
        "/{role_id}",
        description="Безопасное обновление роли",
        dependencies=[Depends(require_rights("roles", "edit"))]
    )
    async def update_role(
        role_id: int,
        name: str | None = Form(None),
        # JSON-строка с правами (нужно отправлять в формате form-data)
        rights_by_goals: str | None = Form(None), # например {"users":["view", "edit"],"roles":["view"]}
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        # Конвертируем JSON-строку из form-data в dict
        if rights_by_goals:
            try:
                rights_by_goals = json.loads(rights_by_goals)
            except json.JSONDecodeError:
                raise HTTPException(
                    400,
                    detail="rights_by_goals должен быть валидным JSON"
                )

        # Получаем роль
        role = (
            db.query(Role)
            .filter(Role.id == role_id)
            .first()
        )
        if not role:
            raise HTTPException(404, "Роль не найдена")

        # Запрещаем редактировать свою собственную роль
        user_role_ids = {ur.role_id for ur in current_user.user_roles}
        if role.id in user_role_ids:
            raise HTTPException(
                status_code=403,
                detail="Нельзя изменять роли, которыми вы обладаете"
            )

        # Обновление имени роли
        if name:
            # Проверка уникальности имени
            exists = db.query(Role).filter(Role.name == name, Role.id != role.id).first()
            if exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Роль с именем '{name}' уже существует"
                )
            role.name = name

        # Права текущего пользователя
        user_rights = current_user.get_rights(db)

        # если передано обновление прав
        if rights_by_goals is not None:

            # Проверяем, что пользователь не выдает прав выше своего уровня
            for goal_name, rights_list in rights_by_goals.items():

                # Проверяем, что цель доступна
                if goal_name not in user_rights:
                    raise HTTPException(
                        status_code=403,
                        detail=f"У вас нет прав на цель '{goal_name}'"
                    )

                # Проверяем каждое право
                for right_name in rights_list:
                    if right_name not in user_rights[goal_name]:
                        raise HTTPException(
                            status_code=403,
                            detail=f"У вас нет права '{right_name}' на цель '{goal_name}'"
                        )

                    # Проверяем, что право существует в таблице прав
                    right_obj = db.query(Right).filter_by(name=right_name).first()
                    if not right_obj:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Право '{right_name}' не существует в системе"
                        )

                # Проверяем, что цель существует
                goal_obj = db.query(Goal).filter_by(name=goal_name).first()
                if not goal_obj:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Цель '{goal_name}' не существует в системе"
                    )

            # Удаляем старые привязки прав
            db.query(RoleRightGoal).filter_by(role_id=role_id).delete()

            # Добавляем новые значения
            for goal_name, rights_list in rights_by_goals.items():
                goal_obj = db.query(Goal).filter_by(name=goal_name).first()

                for right_name in rights_list:
                    right_obj = db.query(Right).filter_by(name=right_name).first()

                    db.add(RoleRightGoal(
                        role_id=role.id,
                        goal_id=goal_obj.id,
                        right_id=right_obj.id
                    ))

        # Сохраняем
        db.commit()
        db.refresh(role)

        # Формируем финальную структуру ответа
        # Новое поле может быть None (если клиент не передал права)
        rights_final = rights_by_goals if rights_by_goals is not None else {}

        # Формируем корректную структуру прав для схемы RoleOut
        return RoleOut(
            id=role.id,
            name=role.name,
            rights_by_goals=rights_final
        )
