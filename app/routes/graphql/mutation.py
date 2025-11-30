import strawberry
from .nav import (
    NavAuditoryType,
    NavCampusType,
    NavFloorType,
    NavLocationType,
    NavPlanType,
    NavStaticType,
    NavTypeType,
    create_nav_auditory,
    create_nav_campus,
    create_nav_floor,
    create_nav_location,
    create_nav_plan,
    create_nav_static,
    create_nav_type,
    delete_nav_auditory,
    delete_nav_campus,
    delete_nav_floor,
    delete_nav_location,
    delete_nav_plan,
    delete_nav_static,
    delete_nav_type,
    update_nav_auditory,
    update_nav_campus,
    update_nav_floor,
    update_nav_location,
    update_nav_plan,
    update_nav_static,
    update_nav_type,
)


@strawberry.type
class Mutation:
    create_nav_floor: NavFloorType = strawberry.mutation(
        resolver=create_nav_floor,
        description="Создать этаж навигации.",
    )
    update_nav_floor: NavFloorType = strawberry.mutation(
        resolver=update_nav_floor,
        description="Обновить этаж навигации.",
    )
    delete_nav_floor: bool = strawberry.mutation(
        resolver=delete_nav_floor,
        description="Удалить этаж навигации.",
    )
    create_nav_location: NavLocationType = strawberry.mutation(
        resolver=create_nav_location,
        description="Создать локацию.",
    )
    update_nav_location: NavLocationType = strawberry.mutation(
        resolver=update_nav_location,
        description="Обновить локацию.",
    )
    delete_nav_location: bool = strawberry.mutation(
        resolver=delete_nav_location,
        description="Удалить локацию.",
    )
    create_nav_campus: NavCampusType = strawberry.mutation(
        resolver=create_nav_campus,
        description="Создать корпус.",
    )
    update_nav_campus: NavCampusType = strawberry.mutation(
        resolver=update_nav_campus,
        description="Обновить корпус.",
    )
    delete_nav_campus: bool = strawberry.mutation(
        resolver=delete_nav_campus,
        description="Удалить корпус.",
    )
    create_nav_plan: NavPlanType = strawberry.mutation(
        resolver=create_nav_plan,
        description="Создать план.",
    )
    update_nav_plan: NavPlanType = strawberry.mutation(
        resolver=update_nav_plan,
        description="Обновить план.",
    )
    delete_nav_plan: bool = strawberry.mutation(
        resolver=delete_nav_plan,
        description="Удалить план.",
    )
    create_nav_static: NavStaticType = strawberry.mutation(
        resolver=create_nav_static,
        description="Создать статический ресурс навигации.",
    )
    update_nav_static: NavStaticType = strawberry.mutation(
        resolver=update_nav_static,
        description="Обновить статический ресурс навигации.",
    )
    delete_nav_static: bool = strawberry.mutation(
        resolver=delete_nav_static,
        description="Удалить статический ресурс навигации.",
    )
    create_nav_type: NavTypeType = strawberry.mutation(
        resolver=create_nav_type,
        description="Создать тип аудитории.",
    )
    update_nav_type: NavTypeType = strawberry.mutation(
        resolver=update_nav_type,
        description="Обновить тип аудитории.",
    )
    delete_nav_type: bool = strawberry.mutation(
        resolver=delete_nav_type,
        description="Удалить тип аудитории.",
    )
    create_nav_auditory: NavAuditoryType = strawberry.mutation(
        resolver=create_nav_auditory,
        description="Создать аудиторию.",
    )
    update_nav_auditory: NavAuditoryType = strawberry.mutation(
        resolver=update_nav_auditory,
        description="Обновить аудиторию.",
    )
    delete_nav_auditory: bool = strawberry.mutation(
        resolver=delete_nav_auditory,
        description="Удалить аудиторию.",
    )
