from fastapi import APIRouter
from .add import register_endpoint as register_add
from .get import register_endpoint as register_get
from .image import register_endpoint as register_image

router = APIRouter(
    prefix="/api/review"
)

register_add(router)
register_get(router)
register_image(router)
