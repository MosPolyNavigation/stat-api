import strawberry
from .event_mutation import EventDictionaryMutation
from .dashboards import (
    DashboardType,
    create_dashboard,
    create_dashboards,
    update_dashboard,
    delete_dashboard,
)
from .dod import (
    DodNavAuditoryType, DodNavCampusType, DodNavFloorType,
    DodNavLocationType, DodNavPlanType, DodNavStaticType,
    DodNavTypeType,
    create_dod_nav_auditory, create_dod_nav_campus,
    create_dod_nav_floor, create_dod_nav_location,
    create_dod_nav_plan, create_dod_nav_static,
    create_dod_nav_type, delete_dod_nav_auditory,
    delete_dod_nav_campus, delete_dod_nav_floor,
    delete_dod_nav_location, delete_dod_nav_plan,
    delete_dod_nav_static, delete_dod_nav_type,
    update_dod_nav_auditory, update_dod_nav_campus,
    update_dod_nav_floor, update_dod_nav_location,
    update_dod_nav_plan, update_dod_nav_static,
    update_dod_nav_type
)
from .nav import (
    NavAuditoryType, NavCampusType, NavFloorType,
    NavLocationType, NavPlanType, NavStaticType,
    NavTypeType,
    create_nav_auditory, create_nav_campus,
    create_nav_floor, create_nav_location,
    create_nav_plan, create_nav_static,
    create_nav_type, delete_nav_auditory,
    delete_nav_campus, delete_nav_floor,
    delete_nav_location, delete_nav_plan,
    delete_nav_static, delete_nav_type,
    update_nav_auditory, update_nav_campus,
    update_nav_floor, update_nav_location,
    update_nav_plan, update_nav_static,
    update_nav_type
)
from .user_role import (
    UserType, RoleType, GrantRoleResult,
    DeleteResult, ChangePasswordResult,
    create_role, create_user,
    grant_role, revoke_role,
    update_user, update_role,
    delete_user, delete_role,
    change_user_password
)
from .logging import graphql_mutation


@strawberry.type
class Mutation(EventDictionaryMutation):
    create_nav_floor: NavFloorType = graphql_mutation(
        resolver=create_nav_floor,
        description="Create navigation floor.",
    )
    update_nav_floor: NavFloorType = graphql_mutation(
        resolver=update_nav_floor,
        description="Update navigation floor.",
    )
    delete_nav_floor: bool = graphql_mutation(
        resolver=delete_nav_floor,
        description="Delete navigation floor.",
    )
    create_nav_location: NavLocationType = graphql_mutation(
        resolver=create_nav_location,
        description="Create navigation location.",
    )
    update_nav_location: NavLocationType = graphql_mutation(
        resolver=update_nav_location,
        description="Update navigation location.",
    )
    delete_nav_location: bool = graphql_mutation(
        resolver=delete_nav_location,
        description="Delete navigation location.",
    )
    create_nav_campus: NavCampusType = graphql_mutation(
        resolver=create_nav_campus,
        description="Create navigation campus.",
    )
    update_nav_campus: NavCampusType = graphql_mutation(
        resolver=update_nav_campus,
        description="Update navigation campus.",
    )
    delete_nav_campus: bool = graphql_mutation(
        resolver=delete_nav_campus,
        description="Delete navigation campus.",
    )
    create_nav_plan: NavPlanType = graphql_mutation(
        resolver=create_nav_plan,
        description="Create navigation plan.",
    )
    update_nav_plan: NavPlanType = graphql_mutation(
        resolver=update_nav_plan,
        description="Update navigation plan.",
    )
    delete_nav_plan: bool = graphql_mutation(
        resolver=delete_nav_plan,
        description="Delete navigation plan.",
    )
    create_nav_static: NavStaticType = graphql_mutation(
        resolver=create_nav_static,
        description="Create navigation static resource.",
    )
    update_nav_static: NavStaticType = graphql_mutation(
        resolver=update_nav_static,
        description="Update navigation static resource.",
    )
    delete_nav_static: bool = graphql_mutation(
        resolver=delete_nav_static,
        description="Delete navigation static resource.",
    )
    create_nav_type: NavTypeType = graphql_mutation(
        resolver=create_nav_type,
        description="Create navigation auditory type.",
    )
    update_nav_type: NavTypeType = graphql_mutation(
        resolver=update_nav_type,
        description="Update navigation auditory type.",
    )
    delete_nav_type: bool = graphql_mutation(
        resolver=delete_nav_type,
        description="Delete navigation auditory type.",
    )
    create_nav_auditory: NavAuditoryType = graphql_mutation(
        resolver=create_nav_auditory,
        description="Create navigation auditory.",
    )
    update_nav_auditory: NavAuditoryType = graphql_mutation(
        resolver=update_nav_auditory,
        description="Update navigation auditory.",
    )
    delete_nav_auditory: bool = graphql_mutation(
        resolver=delete_nav_auditory,
        description="Delete navigation auditory.",
    )

    create_dod_nav_floor: DodNavFloorType = graphql_mutation(
        resolver=create_dod_nav_floor,
        description="Create DOD navigation floor.",
    )
    update_dod_nav_floor: DodNavFloorType = graphql_mutation(
        resolver=update_dod_nav_floor,
        description="Update DOD navigation floor.",
    )
    delete_dod_nav_floor: bool = graphql_mutation(
        resolver=delete_dod_nav_floor,
        description="Delete DOD navigation floor.",
    )
    create_dod_nav_location: DodNavLocationType = graphql_mutation(
        resolver=create_dod_nav_location,
        description="Create DOD navigation location.",
    )
    update_dod_nav_location: DodNavLocationType = graphql_mutation(
        resolver=update_dod_nav_location,
        description="Update DOD navigation location.",
    )
    delete_dod_nav_location: bool = graphql_mutation(
        resolver=delete_dod_nav_location,
        description="Delete DOD navigation location.",
    )
    create_dod_nav_campus: DodNavCampusType = graphql_mutation(
        resolver=create_dod_nav_campus,
        description="Create DOD navigation campus.",
    )
    update_dod_nav_campus: DodNavCampusType = graphql_mutation(
        resolver=update_dod_nav_campus,
        description="Update DOD navigation campus.",
    )
    delete_dod_nav_campus: bool = graphql_mutation(
        resolver=delete_dod_nav_campus,
        description="Delete DOD navigation campus.",
    )
    create_dod_nav_plan: DodNavPlanType = graphql_mutation(
        resolver=create_dod_nav_plan,
        description="Create DOD navigation plan.",
    )
    update_dod_nav_plan: DodNavPlanType = graphql_mutation(
        resolver=update_dod_nav_plan,
        description="Update DOD navigation plan.",
    )
    delete_dod_nav_plan: bool = graphql_mutation(
        resolver=delete_dod_nav_plan,
        description="Delete DOD navigation plan.",
    )
    create_dod_nav_static: DodNavStaticType = graphql_mutation(
        resolver=create_dod_nav_static,
        description="Create DOD navigation static resource.",
    )
    update_dod_nav_static: DodNavStaticType = graphql_mutation(
        resolver=update_dod_nav_static,
        description="Update DOD navigation static resource.",
    )
    delete_dod_nav_static: bool = graphql_mutation(
        resolver=delete_dod_nav_static,
        description="Delete DOD navigation static resource.",
    )
    create_dod_nav_type: DodNavTypeType = graphql_mutation(
        resolver=create_dod_nav_type,
        description="Create DOD navigation auditory type.",
    )
    update_dod_nav_type: DodNavTypeType = graphql_mutation(
        resolver=update_dod_nav_type,
        description="Update DOD navigation auditory type.",
    )
    delete_dod_nav_type: bool = graphql_mutation(
        resolver=delete_dod_nav_type,
        description="Delete DOD navigation auditory type.",
    )
    create_dod_nav_auditory: DodNavAuditoryType = graphql_mutation(
        resolver=create_dod_nav_auditory,
        description="Create DOD navigation auditory.",
    )
    update_dod_nav_auditory: DodNavAuditoryType = graphql_mutation(
        resolver=update_dod_nav_auditory,
        description="Update DOD navigation auditory.",
    )
    delete_dod_nav_auditory: bool = graphql_mutation(
        resolver=delete_dod_nav_auditory,
        description="Delete DOD navigation auditory.",
    )
    create_user: UserType = graphql_mutation(
        resolver=create_user,
        description="Create user."
    )
    update_user: UserType = graphql_mutation(
        resolver=update_user,
        description="Update user."
    )
    delete_user: DeleteResult = graphql_mutation(
        resolver=delete_user,
        description="Delete user."
    )
    change_user_password: ChangePasswordResult = graphql_mutation(
        resolver=change_user_password,
        description="Change user password."
    )
    create_role: RoleType = graphql_mutation(
        resolver=create_role,
        description="Create role."
    )
    update_role: RoleType = graphql_mutation(
        resolver=update_role,
        description="Update role."
    )
    delete_role: DeleteResult = graphql_mutation(
        resolver=delete_role,
        description="Delete role."
    )
    grant_role: GrantRoleResult = graphql_mutation(
        resolver=grant_role,
        description="Grant roles to user."
    )
    revoke_role: GrantRoleResult = graphql_mutation(
        resolver=revoke_role,
        description="Revoke role from user."
    )
    create_dashboard: DashboardType = graphql_mutation(
        resolver=create_dashboard,
        description="Create a new dashboard.",
    )
    create_dashboards: list[DashboardType] = graphql_mutation(
        resolver=create_dashboards,
        description="Create multiple dashboards in a single operation.",
    )
    update_dashboard: DashboardType = graphql_mutation(
        resolver=update_dashboard,
        description="Update an existing dashboard.",
    )
    delete_dashboard: bool = graphql_mutation(
        resolver=delete_dashboard,
        description="Delete a dashboard.",
    )