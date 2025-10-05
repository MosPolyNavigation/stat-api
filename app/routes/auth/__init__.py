from fastapi import APIRouter
from .login import register_endpoint as register_login

router = APIRouter(
    prefix="/api/auth"
)

register_login(router)