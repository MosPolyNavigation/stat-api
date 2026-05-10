import strawberry
from strawberry import relay, Info
from sqlalchemy import select
from graphql import GraphQLError

from app.graphql.core.resource_factory import create_mutation_resource
from app.graphql.core.context import GraphQLContext
from app.graphql.core.permissions import require_permissions, P
from app.graphql.core.logging import GraphQLLoggingExtension

from app.graphql.domains.event_system.resources import (
    EventTypeResource,
    PayloadTypeResource,
    ReviewResource,
)
from app.graphql.domains.event_system.inputs import (
    CreateEventTypeInput, UpdateEventTypeInput,
    CreatePayloadTypeInput, UpdatePayloadTypeInput,
    UpdateReviewInput,
    CreateAllowedPayloadRuleInput, UpdateAllowedPayloadRuleInput,
)
from app.graphql.domains.event_system.types import (
    AllowedPayloadRule as AllowedPayloadRuleType,
)
from app.models import (
    EventType as ETModel,
    PayloadType as PTModel,
    AllowedPayload as APModel,
)

# =============================================================================
# 1. Авто-генерированные мутации (Standard CRUD + Logging)
# =============================================================================
EventTypeMutation = create_mutation_resource(
    EventTypeResource,
    create_input=CreateEventTypeInput,
    update_input=UpdateEventTypeInput,
    name_create="create_event_type",
    name_update="update_event_type",
    name_delete="delete_event_type",
)

PayloadTypeMutation = create_mutation_resource(
    PayloadTypeResource,
    create_input=CreatePayloadTypeInput,
    update_input=UpdatePayloadTypeInput,
    name_create="create_payload_type",
    name_update="update_payload_type",
    name_delete="delete_payload_type",
)

ReviewMutation = create_mutation_resource(
    ReviewResource,
    enable_create=False,  # ⚠️ Только REST
    enable_delete=False,  # ⚠️ Только REST
    update_input=UpdateReviewInput,
    name_update="update_review",
)


# =============================================================================
# 2. Ручные мутации (Составной ключ + кастомная логика)
# =============================================================================
@strawberry.type
class AllowedPayloadRuleMutation:
    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def create_allowed_payload_rule(
            self,
            info: Info,
            data: CreateAllowedPayloadRuleInput,
    ) -> AllowedPayloadRuleType:
        await require_permissions(info, P.STATS_CREATE)
        ctx: GraphQLContext = info.context

        et = await ctx.db.get(ETModel, data.event_type_id)
        pt = await ctx.db.get(PTModel, data.payload_type_id)
        if not et or not pt:
            raise GraphQLError("EventType или PayloadType не найден")

        existing = await ctx.db.execute(
            select(APModel).where(
                APModel.event_type_id == data.event_type_id,
                APModel.payload_type_id == data.payload_type_id,
            )
        )
        if existing.scalar_one_or_none():
            raise GraphQLError("Правило уже существует")

        item = APModel(
            event_type_id=data.event_type_id,
            payload_type_id=data.payload_type_id,
        )
        ctx.db.add(item)
        await ctx.db.commit()

        return AllowedPayloadRuleType(
            event_type_id=item.event_type_id,  # type: ignore[call-arg]
            payload_type_id=item.payload_type_id,  # type: ignore[call-arg]
            _composite_key=f"{item.event_type_id}:{item.payload_type_id}"  # type: ignore[call-arg]
        )

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def update_allowed_payload_rule(
            self,
            info: Info,
            id: relay.GlobalID,
            data: UpdateAllowedPayloadRuleInput,
    ) -> AllowedPayloadRuleType:
        await require_permissions(info, P.STATS_EDIT)
        ctx: GraphQLContext = info.context

        type_name, composite = id.type_name, id.node_id
        if type_name != "AllowedPayloadRule":
            raise GraphQLError(f"Invalid type: expected AllowedPayloadRule, got {type_name}")

        old_event_id, old_payload_id = map(int, composite.split(":"))

        rule = await ctx.db.execute(
            select(APModel).where(
                APModel.event_type_id == old_event_id,
                APModel.payload_type_id == old_payload_id,
            )
        )
        rule_model = rule.scalar_one_or_none()
        if not rule_model:
            raise GraphQLError("Правило не найдено")

        et = await ctx.db.get(ETModel, data.new_event_type_id)
        pt = await ctx.db.get(PTModel, data.new_payload_type_id)
        if not et or not pt:
            raise GraphQLError("Новый EventType или PayloadType не найден")

        conflict = await ctx.db.execute(
            select(APModel).where(
                APModel.event_type_id == data.new_event_type_id,
                APModel.payload_type_id == data.new_payload_type_id,
            )
        )
        if conflict.scalar_one_or_none():
            raise GraphQLError("Такое правило уже существует")

        await ctx.db.delete(rule_model)
        await ctx.db.flush()

        new_rule = APModel(
            event_type_id=data.new_event_type_id,
            payload_type_id=data.new_payload_type_id,
        )
        ctx.db.add(new_rule)
        await ctx.db.commit()

        return AllowedPayloadRuleType(
            event_type_id=new_rule.event_type_id,  # type: ignore[call-arg]
            payload_type_id=new_rule.payload_type_id,  # type: ignore[call-arg]
            _composite_key=f"{new_rule.event_type_id}:{new_rule.payload_type_id}"  # type: ignore[call-arg]
        )

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])
    async def delete_allowed_payload_rule(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> bool:
        await require_permissions(info, P.STATS_DELETE)
        ctx: GraphQLContext = info.context

        type_name, composite = id.type_name, id.node_id
        if type_name != "AllowedPayloadRule":
            raise GraphQLError(f"Invalid type: expected AllowedPayloadRule, got {type_name}")

        event_id, payload_id = map(int, composite.split(":"))

        rule = await ctx.db.execute(
            select(APModel).where(
                APModel.event_type_id == event_id,
                APModel.payload_type_id == payload_id,
            )
        )
        rule_model = rule.scalar_one_or_none()
        if not rule_model:
            raise GraphQLError("Правило не найдено")

        await ctx.db.delete(rule_model)
        await ctx.db.commit()
        return True


# =============================================================================
# 3. Корневой Mutation
# =============================================================================
@strawberry.type
class Mutation(
    EventTypeMutation,
    PayloadTypeMutation,
    ReviewMutation,
    AllowedPayloadRuleMutation,
):
    """
    Корневой Mutation для домена event_system.

    🔹 Авто-генерированные (через фабрику + логирование):
       - create/update/delete_event_type
       - create/update/delete_payload_type
       - create/update/delete_value_type
       - update_review (create/delete отключены)

    🔹 Ручные (составной ключ + валидация + логирование):
       - create/update/delete_allowed_payload_rule
    """
    pass
