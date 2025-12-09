"""Регистрация CRUD эндпоинтов для пользователей."""

from fastapi import APIRouter
from .create import register_endpoint as register_create_user
from .read import register_endpoint as register_read_users
from .update import register_endpoint as register_update_user
from .delete import register_endpoint as register_delete_user
from .change_pass import register_endpoint as register_change_pass

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


register_create_user(router)
register_read_users(router)
register_update_user(router)
register_delete_user(router)
register_change_pass(router)
