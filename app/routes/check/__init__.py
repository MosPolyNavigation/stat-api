from fastapi import APIRouter
from .user_id import register_endpoint as register_client_id

router = APIRouter(
    prefix="/api/check"
)

register_client_id(router)
