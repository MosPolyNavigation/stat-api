"""CRUD-маршруты управления пользователями."""

from fastapi import APIRouter

from .create import register_endpoint as register_create
from .delete import register_endpoint as register_delete
from .read import register_endpoint as register_read
from .update import register_endpoint as register_update

router = APIRouter(prefix="/api/users", tags=["users"])

register_create(router)
register_read(router)
register_update(router)
register_delete(router)
