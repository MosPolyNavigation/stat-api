from app.graphql.core.resource import ResourceConfig, ResourcePermissions
from app.graphql.core.permissions import P
from app.models import (
    EventType as ETModel, PayloadType as PTModel,
    ValueType as VTModel, Review as ReviewModel,
    ClientId as CIModel, Event as EventModel,
    Payload as PayloadModel, DashboardType as DTModel,
    Dashboard as DashboardModel,
)
from app.graphql.domains.event_system.types import (
    EventType as EventTypeType,
    PayloadType as PayloadTypeType,
    ValueType as ValueTypeType,
    DashboardType as DashboardTypeType,
    Dashboard as DashboardType,
    Review as ReviewType,
    ClientId as ClientIdType,
    Event, Payload,
    _event_type_from_model,
    _payload_type_from_model,
    _value_type_from_model,
    _review_from_model,
    _client_id_from_model,
    _event_from_model,
    _payload_from_model,
    _dashboard_from_model,
    _dashboard_type_from_model,
)
from app.graphql.domains.event_system.inputs import (
    EventTypeFilterInput,
    PayloadTypeFilterInput,
    ValueTypeFilterInput,
    ReviewFilterInput,
    ClientIdFilterInput,
    EventFilterInput,
    PayloadFilterInput,
    DashboardFilterInput,
    DashboardTypeFilterInput,
)


# =============================================================================
# Конфигурации ресурсов (подходят для фабрик)
# =============================================================================

EventTypeResource = ResourceConfig(
    model=ETModel,
    graphql_type=EventTypeType,
    filter_input=EventTypeFilterInput,
    convert=_event_type_from_model,  # type: ignore
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.STATS_VIEW,
        create=P.STATS_CREATE,
        edit=P.STATS_EDIT,
        delete=P.STATS_DELETE,
    ),
    enable_logging=True,
    enable_logging_list=False,  # ❌ Не логируем event_types (много запросов)
    enable_logging_get=False,    # ✅ Не логируем event_type
    enable_logging_create=True, # ✅ Логируем создание
    enable_logging_update=True, # ✅ Логируем обновление
    enable_logging_delete=True, # ✅ Логируем удаление
    validators={
        "code_name": lambda v: len(v) <= 20 or "code_name не должен превышать 20 символов",
        "description": lambda v: not v or len(v) <= 100 or "Описание не должно превышать 100 символов",
    }
)

PayloadTypeResource = ResourceConfig(
    model=PTModel,
    graphql_type=PayloadTypeType,
    filter_input=PayloadTypeFilterInput,
    convert=_payload_type_from_model,  # type: ignore
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.STATS_VIEW,
        create=P.STATS_CREATE,
        edit=P.STATS_EDIT,
        delete=P.STATS_DELETE,
    ),
    enable_logging=True,
    enable_logging_list=False,  # ❌ Не логируем payload_types (много запросов)
    enable_logging_get=False,    # ✅ Логируем payload_type
    enable_logging_create=True, # ✅ Логируем создание
    enable_logging_update=True, # ✅ Логируем обновление
    enable_logging_delete=True, # ✅ Логируем удаление
    validators={
        "code_name": lambda v: len(v) <= 20 or "code_name не должен превышать 20 символов",
    }
)

ValueTypeResource = ResourceConfig(
    model=VTModel,
    graphql_type=ValueTypeType,
    filter_input=ValueTypeFilterInput,
    convert=_value_type_from_model,  # type: ignore
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.STATS_VIEW,
        create=P.STATS_CREATE,
        edit=P.STATS_EDIT,
        delete=P.STATS_DELETE,
    ),
    validators={
        "name": lambda v: len(v) <= 20 or "name не должен превышать 20 символов",
    }
)

ClientIdResource = ResourceConfig(
    model=CIModel,
    graphql_type=ClientIdType,
    filter_input=ClientIdFilterInput,
    convert=_client_id_from_model,  # type: ignore
    cursor_field="id",
    order_by=CIModel.creation_date.desc(),
    permissions=ResourcePermissions(
        view=P.STATS_VIEW,
    )
)

ReviewResource = ResourceConfig(
    model=ReviewModel,
    graphql_type=ReviewType,
    filter_input=ReviewFilterInput,
    convert=_review_from_model,
    cursor_field="id",
    order_by=ReviewModel.creation_date.desc(),
    enable_logging=True,
    enable_logging_list=False,
    enable_logging_get=False,
    enable_logging_create=False,
    enable_logging_update=True,
    enable_logging_delete=False,
    permissions=ResourcePermissions(
        view=P.REVIEWS_VIEW,
        edit=P.REVIEWS_EDIT,
    )
)

EventResource = ResourceConfig(
    model=EventModel,
    graphql_type=Event,
    filter_input=EventFilterInput,
    convert=_event_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.STATS_VIEW,
    )
)

PayloadResource = ResourceConfig(
    model=PayloadModel,
    graphql_type=Payload,
    filter_input=PayloadFilterInput,
    convert=_payload_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.STATS_VIEW,
    )
)

DashboardTypeResource = ResourceConfig(
    model=DTModel,
    graphql_type=DashboardTypeType,
    filter_input=DashboardTypeFilterInput,
    convert=_dashboard_type_from_model,
    cursor_field="id",
    permissions=ResourcePermissions(
        view=P.DASHBOARDS_VIEW,
    ),
)

DashboardResource = ResourceConfig(
    model=DashboardModel,
    graphql_type=DashboardType,
    filter_input=DashboardFilterInput,
    convert=_dashboard_from_model,
    cursor_field="id",
    order_by=DashboardModel.dashboard_type_id.desc(),
    permissions=ResourcePermissions(
        view=P.DASHBOARDS_VIEW,
    )
)
