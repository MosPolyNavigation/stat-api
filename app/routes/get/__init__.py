from fastapi import APIRouter
from .user_id import register_endpoint as register_uuid
from .site_endp import register_endpoint as register_site
from .auds_endp import register_endpoint as register_auds
from .ways_endp import register_endpoint as register_ways
from .plans_endp import register_endpoint as register_plans
from .stats_endp import register_endpoint as register_stats
from .popular_endp import register_endpoint as register_popular
from .route_endp import register_endpoint as register_route

router = APIRouter(
    prefix="/api/get"
)

register_uuid(router)
register_site(router)
register_auds(router)
register_ways(router)
register_plans(router)
register_stats(router)
register_popular(router)
register_route(router)
