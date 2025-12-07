"""CRUD-маршруты управления ролями и правами."""

from fastapi import APIRouter

from .assign import register_endpoint as register_assign
from .create import register_endpoint as register_create
from .delete import register_endpoint as register_delete
from .read import register_endpoint as register_read
from .unassign import register_endpoint as register_unassign
from .update import register_endpoint as register_update

router = APIRouter(prefix="/api/roles", tags=["roles"])

register_create(router)
register_read(router)
register_update(router)
register_delete(router)
register_assign(router)
register_unassign(router)
