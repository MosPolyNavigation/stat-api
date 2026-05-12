import strawberry
from app.graphql.core.resource_factory import create_mutation_resource
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
from app.graphql.domains.navigation.inputs import (
    NavLocationInput,
    NavLocationUpdateInput,
    NavCampusInput,
    NavCampusUpdateInput,
    NavFloorInput,
    NavFloorUpdateInput,
    NavTypeInput,
    NavTypeUpdateInput,
    NavPlanInput,
    NavPlanUpdateInput,
    NavAuditoryInput,
    NavAuditoryUpdateInput,
    NavStaticInput,
    NavStaticUpdateInput,
)

LocationMutation = create_mutation_resource(
    LocationResource,
    create_input=NavLocationInput,
    update_input=NavLocationUpdateInput,
    name_create="create_nav_location",
    name_update="update_nav_location",
    name_delete="delete_nav_location",
)

CampusMutation = create_mutation_resource(
    CampusResource,
    create_input=NavCampusInput,
    update_input=NavCampusUpdateInput,
    name_create="create_nav_campus",
    name_update="update_nav_campus",
    name_delete="delete_nav_campus",
)

FloorMutation = create_mutation_resource(
    FloorResource,
    create_input=NavFloorInput,
    update_input=NavFloorUpdateInput,
    name_create="create_nav_floor",
    name_update="update_nav_floor",
    name_delete="delete_nav_floor",
)

TypeMutation = create_mutation_resource(
    TypeResource,
    create_input=NavTypeInput,
    update_input=NavTypeUpdateInput,
    name_create="create_nav_type",
    name_update="update_nav_type",
    name_delete="delete_nav_type",
)

PlanMutation = create_mutation_resource(
    PlanResource,
    create_input=NavPlanInput,
    update_input=NavPlanUpdateInput,
    name_create="create_nav_plan",
    name_update="update_nav_plan",
    name_delete="delete_nav_plan",
)

AuditoryMutation = create_mutation_resource(
    AuditoryResource,
    create_input=NavAuditoryInput,
    update_input=NavAuditoryUpdateInput,
    name_create="create_nav_auditory",
    name_update="update_nav_auditory",
    name_delete="delete_nav_auditory",
)

AudPhotoMutation = create_mutation_resource(
    AudPhotoResource,
    create_input=None,
    update_input=None,
    enable_create=False,
    enable_update=False,
    enable_delete=True,
    name_delete="delete_nav_auditory_photo",
)

StaticMutation = create_mutation_resource(
    StaticResource,
    create_input=NavStaticInput,
    update_input=NavStaticUpdateInput,
    name_create="create_nav_static",
    name_update="update_nav_static",
    name_delete="delete_nav_static",
)


@strawberry.type
class Mutation(
    LocationMutation,
    CampusMutation,
    FloorMutation,
    TypeMutation,
    PlanMutation,
    AuditoryMutation,
    AudPhotoMutation,
    StaticMutation,
):
    """
    Корневой Mutation для домена event_system.

    🔹 Авто-генерированные (через фабрику + логирование):
       - create/update/delete_nav_location
       - create/update/delete_nav_campus
       - create/update/delete_nav_plan
       - create/update/delete_nav_auditory
       - create/update/delete_nav_floor
       - create/update/delete_nav_type
       - create/update/delete_nav_static
       - delete_auditory_photo
    """
    pass
