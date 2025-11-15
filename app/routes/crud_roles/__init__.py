from fastapi import APIRouter
from .create import register_endpoint as register_create_role
from .read import register_endpoint as register_read_roles
from .update import register_endpoint as register_update_role
from .delete import register_endpoint as register_delete_role

router = APIRouter(
    prefix="/api/roles",
    tags=["roles"]
)

register_create_role(router)
register_read_roles(router)
register_update_role(router)
register_delete_role(router)
