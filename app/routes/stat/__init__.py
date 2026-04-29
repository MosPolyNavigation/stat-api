from fastapi import APIRouter
from .event import register_endpoint as register_event

router = APIRouter(prefix="/api/stat")

register_event(router)
