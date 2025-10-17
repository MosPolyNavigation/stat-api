from fastapi import APIRouter
from .user_id import register_endpoint as register_uuid
from .popular_endp import register_endpoint as register_popular
from .route_endp import register_endpoint as register_route

router = APIRouter(
    prefix="/api/get"
)

register_uuid(router)
register_popular(router)
register_route(router)
