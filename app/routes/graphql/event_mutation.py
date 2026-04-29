import strawberry

from .event_dict import (
    AllowedPayloadRuleType,
    EventTypeType,
    PayloadTypeType,
    ValueTypeType,
    create_allowed_payload_rule,
    create_event_type,
    create_payload_type,
    create_value_type,
    delete_allowed_payload_rule,
    delete_event_type,
    delete_payload_type,
    delete_value_type,
    update_allowed_payload_rule,
    update_event_type,
    update_payload_type,
    update_value_type,
)


@strawberry.type
class EventDictionaryMutation:
    create_event_type: EventTypeType = strawberry.mutation(
        resolver=create_event_type,
        description="Create event type.",
    )
    update_event_type: EventTypeType = strawberry.mutation(
        resolver=update_event_type,
        description="Update event type.",
    )
    delete_event_type: bool = strawberry.mutation(
        resolver=delete_event_type,
        description="Delete event type.",
    )
    create_value_type: ValueTypeType = strawberry.mutation(
        resolver=create_value_type,
        description="Create value type.",
    )
    update_value_type: ValueTypeType = strawberry.mutation(
        resolver=update_value_type,
        description="Update value type.",
    )
    delete_value_type: bool = strawberry.mutation(
        resolver=delete_value_type,
        description="Delete value type.",
    )
    create_payload_type: PayloadTypeType = strawberry.mutation(
        resolver=create_payload_type,
        description="Create payload type.",
    )
    update_payload_type: PayloadTypeType = strawberry.mutation(
        resolver=update_payload_type,
        description="Update payload type.",
    )
    delete_payload_type: bool = strawberry.mutation(
        resolver=delete_payload_type,
        description="Delete payload type.",
    )
    create_allowed_payload_rule: AllowedPayloadRuleType = strawberry.mutation(
        resolver=create_allowed_payload_rule,
        description="Create allowed payload rule.",
    )
    update_allowed_payload_rule: AllowedPayloadRuleType = strawberry.mutation(
        resolver=update_allowed_payload_rule,
        description="Update allowed payload rule.",
    )
    delete_allowed_payload_rule: bool = strawberry.mutation(
        resolver=delete_allowed_payload_rule,
        description="Delete allowed payload rule.",
    )
