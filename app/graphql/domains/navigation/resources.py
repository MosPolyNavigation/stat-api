import json
from typing import Callable, Any
from app.graphql.core.resource import ResourceConfig, ResourcePermissions
from app.graphql.core.permissions import P
from app.graphql.domains.navigation.inputs import (
    NavLocationFilterInput,
    NavLocationOrderByInput,
    NavCampusFilterInput,
    NavCampusOrderByInput,
    NavFloorFilterInput,
    NavFloorOrderByInput,
    NavTypeFilterInput,
    NavTypeOrderByInput,
    NavPlanFilterInput,
    NavPlanOrderByInput,
    NavAuditoryFilterInput,
    NavAuditoryOrderByInput,
    NavAuditoryPhotoFilterInput,
    NavAuditoryPhotoOrderByInput,
    NavStaticFilterInput,
    NavStaticOrderByInput,
)
from app.graphql.domains.navigation.types import (
    NavLocation as NavLocationType,
    NavCampus as NavCampusType,
    NavFloor as NavFloorType,
    NavType as NavTypeType,
    NavPlan as NavPlanType,
    NavAuditory as NavAuditoryType,
    NavAuditoryPhoto as NavAuditoryPhotoType,
    NavStatic as NavStaticType,
    _location_from_model,
    _campus_from_model,
    _floor_from_model,
    _type_from_model,
    _plan_from_model,
    _auditory_from_model,
    _aud_photo_from_model,
    _static_from_model,
)
from app.models import (
    Location as LModel,
    Corpus as CModel,
    Floor as FModel,
    Type as NTModel,
    Plan as PModel,
    Auditory as AModel,
    AudPhoto as APModel,
    Static as SModel,
)


def _json_array_validator(field_name: str) -> Callable[[Any], bool | str]:
    """Валидатор для полей, хранящих JSON-массивы."""

    def validator(value: Any) -> bool | str:
        if value is None:
            return True
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                return f"{field_name} должен быть JSON-массивом"
        except (json.JSONDecodeError, ValueError):
            return f"{field_name} содержит невалидный JSON"
        return True

    return validator


def _json_validator(field_name: str) -> Callable[[Any], bool | str]:
    """Валидатор для любых JSON полей."""

    def validator(value: Any) -> bool | str:
        if value is None:
            return True
        try:
            json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return f"{field_name} содержит невалидный JSON"
        return True

    return validator


LocationResource = ResourceConfig(
    model=LModel,
    graphql_type=NavLocationType,
    filter_input=NavLocationFilterInput,
    order_by_input=NavLocationOrderByInput,
    convert=_location_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    validators={"crossings": _json_array_validator("crossings")},
    enable_logging=True,
)

CampusResource = ResourceConfig(
    model=CModel,
    graphql_type=NavCampusType,
    filter_input=NavCampusFilterInput,
    order_by_input=NavCampusOrderByInput,
    convert=_campus_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    validators={"stair_groups": _json_array_validator("stair_groups")},
    enable_logging=True,
)

FloorResource = ResourceConfig(
    model=FModel,
    graphql_type=NavFloorType,
    filter_input=NavFloorFilterInput,
    order_by_input=NavFloorOrderByInput,
    convert=_floor_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    enable_logging=True,
)

TypeResource = ResourceConfig(
    model=NTModel,
    graphql_type=NavTypeType,
    filter_input=NavTypeFilterInput,
    order_by_input=NavTypeOrderByInput,
    convert=_type_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    enable_logging=True,
)

PlanResource = ResourceConfig(
    model=PModel,
    graphql_type=NavPlanType,
    filter_input=NavPlanFilterInput,
    order_by_input=NavPlanOrderByInput,
    convert=_plan_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    validators={
        "entrances": _json_array_validator("entrances"),
        "graph": _json_array_validator("graph"),
    },
    enable_logging=True,
)

AuditoryResource = ResourceConfig(
    model=AModel,
    graphql_type=NavAuditoryType,
    filter_input=NavAuditoryFilterInput,
    order_by_input=NavAuditoryOrderByInput,
    convert=_auditory_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    enable_logging=True,
)

AudPhotoResource = ResourceConfig(
    model=APModel,
    graphql_type=NavAuditoryPhotoType,
    filter_input=NavAuditoryPhotoFilterInput,
    order_by_input=NavAuditoryPhotoOrderByInput,
    convert=_aud_photo_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    enable_logging=True,
)

StaticResource = ResourceConfig(
    model=SModel,
    graphql_type=NavStaticType,
    filter_input=NavStaticFilterInput,
    order_by_input=NavStaticOrderByInput,
    convert=_static_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.NAV_VIEW, create=P.NAV_CREATE, edit=P.NAV_EDIT, delete=P.NAV_DELETE
    ),
    enable_logging=True,
)
