import strawberry
from app.graphql.core.resource_factory import create_query_resource
from app.graphql.domains.navigation.resources import (
    LocationResource,
    CampusResource,
    FloorResource,
    TypeResource,
    PlanResource,
    AuditoryResource,
    AudPhotoResource,
    StaticResource,
)


LocationQuery = create_query_resource(
    LocationResource, name_list="nav_locations", name_get="nav_location"
)

CampusQuery = create_query_resource(
    CampusResource, name_list="nav_campuses", name_get="nav_campus"
)

FloorQuery = create_query_resource(
    FloorResource, name_list="nav_floors", name_get="nav_floor"
)

TypeQuery = create_query_resource(
    TypeResource, name_list="nav_types", name_get="nav_type"
)

PlanQuery = create_query_resource(
    PlanResource, name_list="nav_plans", name_get="nav_plan"
)

AuditoryQuery = create_query_resource(
    AuditoryResource, name_list="nav_auditories", name_get="nav_auditory"
)

AudPhotoQuery = create_query_resource(
    AudPhotoResource, name_list="nav_auditory_photos", name_get="nav_auditory_photo"
)

StaticQuery = create_query_resource(
    StaticResource, name_list="nav_statics", name_get="nav_static"
)


@strawberry.type
class Query(
    LocationQuery,
    CampusQuery,
    FloorQuery,
    TypeQuery,
    PlanQuery,
    AuditoryQuery,
    AudPhotoQuery,
    StaticQuery,
):
    """
    Корневой Query для домена navigation.

    Авто-генерированные методы:
    - nav_locations / nav_location
    - nav_campuses / nav_campus
    - nav_floors / nav_floor
    - nav_types / nav_type
    - nav_plans / nav_plan
    - nav_auditories / nav_auditory
    - nav_auditory_photos / nav_auditory_photo
    - nav_statics / nav_static
    """

    pass
