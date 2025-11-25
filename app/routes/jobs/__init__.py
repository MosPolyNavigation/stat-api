from fastapi import APIRouter
from .schedule import register_endpoint as register_schedule

router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"]
)

register_schedule(router)
