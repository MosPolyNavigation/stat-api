from fastapi import APIRouter
from .popular_endp import register_endpoint as register_popular
from .route_endp import register_endpoint as register_route
from .schedule import register_endpoint as register_schedule
from .location_data_endp import register_endpoint as register_location_data
from .event_type import register_endpoint as register_event_type
from .payload_type import register_endpoint as register_payload_type
from .user_id import register_endpoint as register_user_id

router = APIRouter(
    prefix="/api/get"
)

register_popular(router)
register_route(router)
register_schedule(router)
register_location_data(router)
register_event_type(router)
register_payload_type(router)
# TODO: Удалить, как фронты перейдут на новую схему событий
register_user_id(router)
