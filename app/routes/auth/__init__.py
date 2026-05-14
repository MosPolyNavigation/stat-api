from fastapi import APIRouter
from .login import register_endpoint as register_login
from .change_pass import register_endpoint as register_change_pass
from .revoke import register_endpoint as register_revoke
from .allowed_perms import register_endpoint as register_allowed_perms

router = APIRouter(prefix="/api/auth")

register_login(router)
register_change_pass(router)
register_revoke(router)
register_allowed_perms(router)
