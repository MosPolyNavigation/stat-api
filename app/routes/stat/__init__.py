"""Регистрация маршрутов статистики."""

from fastapi import APIRouter

from .aud import register_endpoint as register_aud
from .plan import register_endpoint as register_plan
from .site import register_endpoint as register_site
from .way import register_endpoint as register_way

router = APIRouter(prefix="/api/stat")

register_site(router)
register_aud(router)
register_way(router)
register_plan(router)
