"""Маршруты валидации данных."""

from fastapi import APIRouter

from .user_id import register_endpoint as register_user_id

router = APIRouter(prefix="/api/check")

register_user_id(router)
