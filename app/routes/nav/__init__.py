from fastapi import APIRouter
from .campuses import register_endpoint as register_nav_campuses
from .campus import register_endpoint as register_nav_campus
from .plan import register_endpoint as register_nav_plan

router = APIRouter(
    prefix="/api/nav",
    tags=["nav"],
)

register_nav_campuses(router)
register_nav_campus(router)
register_nav_plan(router)