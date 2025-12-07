"""Регистрация публичных GET-маршрутов."""

from fastapi import APIRouter

from .popular_endp import register_endpoint as register_popular
from .route_endp import register_endpoint as register_route
from .schedule import register_endpoint as register_schedule
from .user_id import register_endpoint as register_uuid

router = APIRouter(prefix="/api/get")

register_uuid(router)
register_popular(router)
register_route(router)
register_schedule(router)
