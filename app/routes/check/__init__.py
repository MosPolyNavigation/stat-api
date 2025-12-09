"""Регистрация проверочных эндпоинтов."""

from fastapi import APIRouter
from .user_id import register_endpoint as register_uuid

router = APIRouter(
    prefix="/api/check"
)

register_uuid(router)
