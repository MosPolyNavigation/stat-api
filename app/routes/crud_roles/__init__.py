"""Регистрация CRUD эндпоинтов для ролей и прав."""

from fastapi import APIRouter
from .create import register_endpoint as register_create_role
from .read import register_endpoint as register_read_roles
from .update import register_endpoint as register_update_role
from .delete import register_endpoint as register_delete_role

from .assign import register_endpoint as assign_role
from .unassign import register_endpoint as unassign_role

router = APIRouter(
    prefix="/api/roles",
    tags=["roles"]
)

register_create_role(router)
register_read_roles(router)
register_update_role(router)
register_delete_role(router)

assign_role(router)
unassign_role(router)
