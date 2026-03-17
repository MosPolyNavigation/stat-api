from fastapi import APIRouter
from .admin import register_endpoint

router = APIRouter(
    prefix="/api/admin"
)

register_endpoint(router)
