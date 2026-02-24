from fastapi import APIRouter
from .schedule import register_endpoint as register_schedule
from .location_data import register_endpoint as register_locationData

router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"]
)

register_schedule(router)
register_locationData(router)
