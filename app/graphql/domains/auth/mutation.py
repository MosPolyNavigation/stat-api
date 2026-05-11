import strawberry
from strawberry import Info
from sqlalchemy import select, delete, func
from graphql import GraphQLError
from datetime import datetime
from pwdlib import PasswordHash

from app.graphql.core.context import GraphQLContext
from app.graphql.core.permissions import require_permissions, P
from app.graphql.core.logging import GraphQLLoggingExtension
from app.graphql.domains.auth.inputs import (
    CreateUserInput,
    UpdateUserInput,
    ChangeUserPasswordInput,
    CreateRoleInput,
    UpdateRoleInput,
    GrantRoleInput
)
from app.graphql.domains.auth.types import (
    User as UserType,
    Role as RoleType,
    _user_from_model,
    _role_from_model,
)
from app.models.auth.user import User
from app.models.auth.role import Role
from app.models.auth.user_role import UserRole
from app.models.auth.role_right_goal import RoleRightGoal
from app.services.permission_service import PermissionService

# Хэшер паролей (вынесен на уровень модуля для переиспользования)
password_hash = PasswordHash.recommended()


# =============================================================================
# Кастомные мутации: User
# =============================================================================
@strawberry.type
class UserMutation:
    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def create_user(self, info: Info, data: CreateUserInput) -> UserType:
        await require_permissions(info, P.USERS_CREATE)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        logger = info.context["user_logger"]

        existing = await ctx.db.execute(select(User).where(User.login == data.login))
        if existing.scalar_one_or_none():
            raise GraphQLError("Пользователь с таким логином уже существует")

        user = User(
            login=data.login,
            hash=password_hash.hash(data.password),
            fio=data.fio,
            is_active=data.is_active
        )
        ctx.db.add(user)
        await ctx.db.commit()
        await ctx.db.refresh(user)

        logger.log(current_user, f"Создание пользователя {user.login}")
        return _user_from_model(user)

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def update_user(self, info: Info, id: int, data: UpdateUserInput) -> UserType:
        await require_permissions(info, P.USERS_EDIT)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        logger = info.context["user_logger"]

        user = await ctx.db.get(User, id)
        if not user:
            raise GraphQLError(f"Пользователь с ID {id} не найден")

        if user.id == current_user.id and data.is_active is False:
            raise GraphQLError("Нельзя деактивировать самого себя.")

        if data.fio is not None:
            user.fio = data.fio
        if data.is_active is not None:
            user.is_active = data.is_active

        await ctx.db.commit()
        await ctx.db.refresh(user)
        logger.log(current_user, f"Обновление пользователя {user.login}")

        return _user_from_model(user)  # noqa

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def delete_user(self, info: Info, id: int) -> bool:
        await require_permissions(info, P.USERS_DELETE)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        logger = info.context["user_logger"]

        user = await ctx.db.get(User, id)
        if not user:
            raise GraphQLError(f"Пользователь с ID {id} не найден")
        if user.id == current_user.id:
            raise GraphQLError("Нельзя удалить самого себя")

        await ctx.db.delete(user)
        await ctx.db.commit()
        logger.log(current_user, f"Удален пользователь {user.login}")
        return True

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def change_user_password(self, info: Info, data: ChangeUserPasswordInput) -> bool:
        await require_permissions(info, P.USER_PASS_EDIT)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        logger = info.context["user_logger"]

        user = await ctx.db.get(User, data.user_id)
        if not user:
            raise GraphQLError(f"Пользователь с ID {data.user_id} не найден")
        if user.id == current_user.id:
            raise GraphQLError("Используйте REST endpoint для смены собственного пароля.")
        if len(data.new_password) < 8:
            raise GraphQLError("Пароль должен содержать минимум 8 символов")

        user.hash = password_hash.hash(data.new_password)
        user.updated_at = datetime.now()
        await ctx.db.commit()
        logger.log(current_user, f"Изменен пароль для {user.login}")
        return True


# =============================================================================
# Кастомные мутации: Role
# =============================================================================
@strawberry.type
class RoleMutation:
    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def create_role(self, info: Info, data: CreateRoleInput) -> RoleType:
        await require_permissions(info, P.ROLES_CREATE)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        service: PermissionService = info.context["permission_service"]
        logger = info.context["user_logger"]

        existing = await ctx.db.execute(select(Role).where(Role.name == data.name))
        if existing.scalar_one_or_none():
            raise GraphQLError("Роль с таким названием уже существует")

        if data.role_right_goals:
            required = [(r.right_id, r.goal_id) for r in data.role_right_goals]
            missing = await service.check_grant_permissions(current_user.id, required)
            if missing:
                raise GraphQLError(f"Недостаточно прав для назначения: {', '.join(missing)}")

        role = Role(name=data.name)
        ctx.db.add(role)
        await ctx.db.flush()

        if data.role_right_goals:
            ctx.db.add_all([RoleRightGoal(
                role_id=role.id, right_id=rrg.right_id,
                goal_id=rrg.goal_id, can_grant=rrg.can_grant
            ) for rrg in data.role_right_goals])
        await ctx.db.commit()
        await ctx.db.refresh(role)
        logger.log(current_user, f"Создана роль {role.name}")
        return _role_from_model(role)

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def update_role(self, info: Info, id: int, data: UpdateRoleInput) -> RoleType:
        await require_permissions(info, P.ROLES_EDIT)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        service: PermissionService = info.context["permission_service"]
        logger = info.context["user_logger"]

        if id == 1:
            raise GraphQLError("Нельзя изменить роль с ID 1")
        role = await ctx.db.get(Role, id)
        if not role:
            raise GraphQLError(f"Роль с ID {id} не найдена")

        if data.name is not None:
            dup = await ctx.db.execute(select(Role).where(Role.name == data.name, Role.id != id))
            if dup.scalar_one_or_none():
                raise GraphQLError("Роль с таким названием уже существует")
            role.name = data.name

        if data.role_right_goals is not None:
            required = [(r.right_id, r.goal_id) for r in data.role_right_goals]
            missing = await service.check_grant_permissions(current_user.id, required)
            if missing:
                raise GraphQLError(f"Недостаточно прав для назначения: {', '.join(missing)}")

            await ctx.db.execute(
                delete(RoleRightGoal).where(RoleRightGoal.role_id == id)
            )

            ctx.db.add_all([RoleRightGoal(
                role_id=id,
                right_id=rrg.right_id,
                goal_id=rrg.goal_id,
                can_grant=rrg.can_grant
            ) for rrg in data.role_right_goals])
        await ctx.db.commit()
        await ctx.db.refresh(role)
        logger.log(current_user, f"Обновлена роль {role.name}")
        return _role_from_model(role)  # noqa

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def delete_role(self, info: Info, id: int) -> bool:
        await require_permissions(info, P.ROLES_DELETE)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        service: PermissionService = info.context["permission_service"]
        logger = info.context["user_logger"]

        if id == 1:
            raise GraphQLError("Нельзя удалить роль с ID 1")
        role = await ctx.db.get(Role, id)
        if not role:
            raise GraphQLError(f"Роль с ID {id} не найдена")

        count = await ctx.db.execute(
            select(func.count()).select_from(UserRole).where(UserRole.role_id == id)
        )
        if count.scalar() > 0:  # noqa
            raise GraphQLError("Роль назначена пользователям. Сначала отзовите её.")

        rights = await ctx.db.execute(select(RoleRightGoal).where(RoleRightGoal.role_id == id))
        if rights.scalars().all():
            req = list({(r.right_id, r.goal_id) for r in rights.scalars()})
            missing = await service.check_grant_permissions(current_user.id, req)
            if missing:
                raise GraphQLError(f"Недостаточно прав для удаления роли: {', '.join(missing)}")

        await ctx.db.delete(role)
        await ctx.db.commit()
        logger.log(current_user, f"Удалена роль {id}")
        return True


# =============================================================================
# Кастомные мутации: UserRole (Grant/Revoke)
# =============================================================================
@strawberry.type
class UserRoleMutation:
    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def grant_role(self, info: Info, data: GrantRoleInput) -> bool:
        await require_permissions(info, P.ROLES_EDIT)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        service: PermissionService = info.context["permission_service"]
        logger = info.context["user_logger"]

        target = await ctx.db.get(User, data.user_id)
        if not target:
            raise GraphQLError(f"Пользователь {data.user_id} не найден")
        if not target.is_active:
            raise GraphQLError("Нельзя назначить роль неактивному пользователю")

        roles = await ctx.db.execute(select(Role).where(Role.id.in_(data.role_ids)))
        found_ids = {r.id for r in roles.scalars()}
        if missing := set(data.role_ids) - found_ids:
            raise GraphQLError(f"Роли не найдены: {missing}")

        rrgs = await ctx.db.execute(select(RoleRightGoal).where(RoleRightGoal.role_id.in_(found_ids)))
        perms = list({(r.right_id, r.goal_id) for r in rrgs.scalars()})
        if missing_perms := await service.check_grant_permissions(current_user.id, perms):
            raise GraphQLError(f"Эскалация привилегий. Нет прав: {', '.join(missing_perms)}")

        existing_result = await ctx.db.execute(
            select(UserRole.role_id).where(UserRole.user_id == data.user_id)
        )
        existing_role_ids = set(existing_result.scalars().all())
        roles_to_assign = [rid for rid in data.role_ids if rid not in existing_role_ids]

        if roles_to_assign:
            ctx.db.add_all([
                UserRole(user_id=data.user_id, role_id=rid)
                for rid in roles_to_assign
            ])

        await ctx.db.commit()
        logger.log(current_user, f"Назначены роли {data.role_ids} пользователю {data.user_id}")
        return True

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def revoke_role(self, info: Info, user_id: int, role_id: int) -> bool:
        await require_permissions(info, P.ROLES_EDIT)
        ctx: GraphQLContext = info.context
        current_user = info.context["current_user"]
        service: PermissionService = info.context["permission_service"]
        logger = info.context["user_logger"]

        rrgs = await ctx.db.execute(select(RoleRightGoal).where(RoleRightGoal.role_id == role_id))
        perms = list({(r.right_id, r.goal_id) for r in rrgs.scalars()})
        if missing := await service.check_grant_permissions(current_user.id, perms):
            raise GraphQLError(f"Недостаточно прав для отзыва: {', '.join(missing)}")

        ur = await ctx.db.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        link = ur.scalar_one_or_none()
        if not link:
            raise GraphQLError("Связь пользователь-роль не найдена")

        await ctx.db.delete(link)
        await ctx.db.commit()
        logger.log(current_user, f"Отозвана роль {role_id} у пользователя {user_id}")
        return True


# =============================================================================
# Корневой Mutation
# =============================================================================
@strawberry.type
class Mutation(
    UserMutation,
    RoleMutation,
    UserRoleMutation,
):
    """Корневой Mutation для домена auth."""
    pass
