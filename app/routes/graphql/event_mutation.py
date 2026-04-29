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
        description="Создать тип события.",
    )
    update_event_type: EventTypeType = strawberry.mutation(
        resolver=update_event_type,
        description="Обновить тип события.",
    )
    delete_event_type: bool = strawberry.mutation(
        resolver=delete_event_type,
        description="Удалить тип события.",
    )
    create_value_type: ValueTypeType = strawberry.mutation(
        resolver=create_value_type,
        description="Создать тип значения.",
    )
    update_value_type: ValueTypeType = strawberry.mutation(
        resolver=update_value_type,
        description="Обновить тип значения.",
    )
    delete_value_type: bool = strawberry.mutation(
        resolver=delete_value_type,
        description="Удалить тип значения.",
    )
    create_payload_type: PayloadTypeType = strawberry.mutation(
        resolver=create_payload_type,
        description="Создать тип payload.",
    )
    update_payload_type: PayloadTypeType = strawberry.mutation(
        resolver=update_payload_type,
        description="Обновить тип payload.",
    )
    delete_payload_type: bool = strawberry.mutation(
        resolver=delete_payload_type,
        description="Удалить тип payload.",
    )
    create_allowed_payload_rule: AllowedPayloadRuleType = strawberry.mutation(
        resolver=create_allowed_payload_rule,
        description="Создать правило допустимого payload.",
    )
    update_allowed_payload_rule: AllowedPayloadRuleType = strawberry.mutation(
        resolver=update_allowed_payload_rule,
        description="Обновить правило допустимого payload.",
    )
    delete_allowed_payload_rule: bool = strawberry.mutation(
        resolver=delete_allowed_payload_rule,
        description="Удалить правило допустимого payload.",
    )
