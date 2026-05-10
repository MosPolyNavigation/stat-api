from typing import Optional, List
import strawberry
from app.graphql.core.filters import BaseFilterInput, StringFilterInput, IntFilterInput


# =============================================================================
# Фильтры (наследуют BaseFilterInput для apply_filters)
# =============================================================================
@strawberry.input
class EventTypeFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    code_name: Optional[StringFilterInput] = None
    # Логические группы
    and_: Optional[List["EventTypeFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["EventTypeFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["EventTypeFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class PayloadTypeFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    code_name: Optional[StringFilterInput] = None
    value_type_id: Optional[IntFilterInput] = None
    and_: Optional[List["PayloadTypeFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["PayloadTypeFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["PayloadTypeFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class ValueTypeFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    name: Optional[StringFilterInput] = None
    and_: Optional[List["ValueTypeFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["ValueTypeFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["ValueTypeFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class AllowedPayloadRuleFilterInput(BaseFilterInput):
    event_type_id: Optional[IntFilterInput] = None
    payload_type_id: Optional[IntFilterInput] = None
    and_: Optional[List["AllowedPayloadRuleFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["AllowedPayloadRuleFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["AllowedPayloadRuleFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class ReviewFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    client_id: Optional[IntFilterInput] = None
    problem_id: Optional[StringFilterInput] = None
    review_status_id: Optional[IntFilterInput] = None
    text: Optional[StringFilterInput] = None
    and_: Optional[List["ReviewFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["ReviewFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["ReviewFilterInput"] = strawberry.field(name="not", default=None)


# =============================================================================
# Mutation Inputs (простые dataclass, не фильтры)
# =============================================================================
@strawberry.input
class CreateEventTypeInput:
    code_name: str
    description: Optional[str] = None


@strawberry.input
class UpdateEventTypeInput:
    code_name: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class CreatePayloadTypeInput:
    code_name: str
    value_type_id: int
    description: Optional[str] = None


@strawberry.input
class UpdatePayloadTypeInput:
    code_name: Optional[str] = None
    value_type_id: Optional[int] = None
    description: Optional[str] = None


@strawberry.input
class CreateAllowedPayloadRuleInput:
    event_type_id: int
    payload_type_id: int


@strawberry.input
class UpdateAllowedPayloadRuleInput:
    new_event_type_id: int
    new_payload_type_id: int


@strawberry.input
class UpdateReviewInput:
    problem_id: Optional[str] = None
    status_id: Optional[int] = None
    text: Optional[str] = None
    image_name: Optional[str] = None


@strawberry.input
class ClientIdFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    ident: Optional[StringFilterInput] = None
    and_: Optional[List["ClientIdFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["ClientIdFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["ClientIdFilterInput"] = strawberry.field(name="not", default=None)


# =============================================================================
# Event & Payload Filters
# =============================================================================
@strawberry.input
class EventFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    client_id: Optional[IntFilterInput] = None
    event_type_id: Optional[IntFilterInput] = None
    and_: Optional[List["EventFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["EventFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["EventFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class PayloadFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    event_id: Optional[IntFilterInput] = None
    type_id: Optional[IntFilterInput] = None
    value: Optional[StringFilterInput] = None
    and_: Optional[List["PayloadFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["PayloadFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["PayloadFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class DashboardTypeFilterInput(BaseFilterInput):
    id: Optional[IntFilterInput] = None
    code_name: Optional[StringFilterInput] = None
    and_: Optional[List["DashboardTypeFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["DashboardTypeFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["DashboardTypeFilterInput"] = strawberry.field(name="not", default=None)


@strawberry.input
class DashboardTypeInput:
    """Инпут для создания/обновления дашборда."""
    display_order: int
    event_type_id: int
    dashboard_type_id: int
    title_text: str


@strawberry.input
class DashboardFilterInput(BaseFilterInput):
    """Фильтр для списка дашбордов."""
    dashboard_type_id: Optional[IntFilterInput] = None
    event_type_id: Optional[IntFilterInput] = None
    title_text: Optional[StringFilterInput] = None
    # Логические операторы
    and_: Optional[List["DashboardFilterInput"]] = strawberry.field(name="and", default=None)
    or_: Optional[List["DashboardFilterInput"]] = strawberry.field(name="or", default=None)
    not_: Optional["DashboardFilterInput"] = strawberry.field(name="not", default=None)
