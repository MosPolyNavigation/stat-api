"""Регистрация статистических REST-эндпоинтов."""

from fastapi import APIRouter
from .site import register_endpoint as register_site
from .aud import register_endpoint as register_aud
from .way import register_endpoint as register_way
from .plan import register_endpoint as register_plan
from .tg_bot import register_endpoint as register_tg_bot

router = APIRouter(
    prefix="/api/stat"
)

register_site(router)
register_aud(router)
register_way(router)
register_plan(router)
register_tg_bot(router)
