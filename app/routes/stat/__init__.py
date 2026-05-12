from fastapi import APIRouter
from app.routes.stat.client import register_endpoint as register_client_endpoint
from app.routes.stat.event import register_endpoint as register_event_endpoint
from app.routes.stat.old_events import register_endpoints as register_old_endpoints

router = APIRouter(prefix="/api/stat")

register_client_endpoint(router)
register_event_endpoint(router)
# TODO: Удалить, как фронты перейдут на новую схему событий
register_old_endpoints(router)
