"""Маршруты управления фоновыми задачами."""

from fastapi import APIRouter

from .schedule import register_endpoint as register_schedule

router = APIRouter(prefix="/api/jobs")

register_schedule(router)
