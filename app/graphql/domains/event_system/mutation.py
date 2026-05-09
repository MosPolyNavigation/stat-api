import strawberry
from strawberry import Info, relay
from graphql import GraphQLError
from sqlalchemy import select

from app.models import (
    EventType as ETModel,
    PayloadType as PTModel,
    ValueType as VTModel,
    AllowedPayload as APModel,
    Review as ReviewModel,
)
from app.graphql.core.permissions import require_permissions, P

from .types import (
    EventType as EventTypeType,
    PayloadType as PayloadTypeType,
    ValueType as ValueTypeType,
    AllowedPayloadRule as AllowedPayloadRuleType,
    ReviewType,
)
from .inputs import (
    CreateEventTypeInput, UpdateEventTypeInput,
    CreatePayloadTypeInput, UpdatePayloadTypeInput,
    CreateAllowedPayloadRuleInput, UpdateAllowedPayloadRuleInput,
    UpdateReviewInput,
)


# =============================================================================
# Helper: локальные конвертеры (для консистентности с types.py)
# =============================================================================
def _event_type_from_model(model: ETModel) -> EventTypeType:
    return EventTypeType(
        db_id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _payload_type_from_model(model: PTModel) -> PayloadTypeType:
    return PayloadTypeType(
        db_id=model.id,  # type: ignore[call-arg]
        code_name=model.code_name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
        value_type_id=model.value_type_id,  # type: ignore[call-arg]
    )


def _value_type_from_model(model: VTModel) -> ValueTypeType:
    return ValueTypeType(
        db_id=model.id,  # type: ignore[call-arg]
        name=model.name,  # type: ignore[call-arg]
        description=model.description,  # type: ignore[call-arg]
    )


def _review_from_model(model: ReviewModel) -> ReviewType:
    return ReviewType(
        db_id=model.id,  # type: ignore[call-arg]
        client_id=model.client_id,  # type: ignore[call-arg]
        problem_id=model.problem_id,  # type: ignore[call-arg]
        status_id=model.review_status_id,  # type: ignore[call-arg]
        text=model.text,  # type: ignore[call-arg]
        image_name=model.image_name,  # type: ignore[call-arg]
        creation_date=model.creation_date,  # type: ignore[call-arg]
    )


@strawberry.type
class Mutation:
    # -------------------------------------------------------------------------
    # EventType Mutations
    # -------------------------------------------------------------------------
    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def create_event_type(
            self,
            info: Info,
            data: CreateEventTypeInput,
    ) -> EventTypeType:
        await require_permissions(info, P.STATS_CREATE)
        ctx = info.context

        item = ETModel(code_name=data.code_name, description=data.description)
        ctx.db.add(item)
        await ctx.db.commit()
        await ctx.db.refresh(item)
        return _event_type_from_model(item)

    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def update_event_type(
            self,
            info: Info,
            id: relay.GlobalID,
            data: UpdateEventTypeInput,
    ) -> EventTypeType:
        await require_permissions(info, P.STATS_EDIT)
        ctx = info.context

        node = await id.resolve_node(info, ensure_type=EventTypeType)
        if not node:
            raise GraphQLError(f"EventType {id} not found")

        model = await ctx.db.get(ETModel, node.db_id)
        if not model:
            raise GraphQLError(f"EventType {node.db_id} not found in DB")

        if data.code_name is not None:
            model.code_name = data.code_name
        if data.description is not None:
            model.description = data.description

        await ctx.db.commit()
        await ctx.db.refresh(model)
        return _event_type_from_model(model)

    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def delete_event_type(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> bool:
        await require_permissions(info, P.STATS_DELETE)
        ctx = info.context

        node = await id.resolve_node(info, ensure_type=EventTypeType)
        if not node:
            raise GraphQLError(f"EventType {id} not found")

        model = await ctx.db.get(ETModel, node.db_id)
        if model:
            await ctx.db.delete(model)
            await ctx.db.commit()
        return True

    # -------------------------------------------------------------------------
    # PayloadType Mutations
    # -------------------------------------------------------------------------
    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def create_payload_type(
            self,
            info: Info,
            data: CreatePayloadTypeInput,
    ) -> PayloadTypeType:
        await require_permissions(info, P.STATS_CREATE)
        ctx = info.context

        vt = await ctx.db.get(VTModel, data.value_type_id)
        if not vt:
            raise GraphQLError(f"ValueType {data.value_type_id} not found")

        item = PTModel(
            code_name=data.code_name,
            value_type_id=data.value_type_id,
            description=data.description,
        )
        ctx.db.add(item)
        await ctx.db.commit()
        await ctx.db.refresh(item)
        return _payload_type_from_model(item)

    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def update_payload_type(
            self,
            info: Info,
            id: relay.GlobalID,
            data: UpdatePayloadTypeInput,
    ) -> PayloadTypeType:
        await require_permissions(info, P.STATS_EDIT)
        ctx = info.context

        node = await id.resolve_node(info, ensure_type=PayloadTypeType)
        if not node:
            raise GraphQLError(f"PayloadType {id} not found")

        model = await ctx.db.get(PTModel, node.db_id)
        if not model:
            raise GraphQLError(f"PayloadType {node.db_id} not found in DB")

        if data.value_type_id is not None:
            vt = await ctx.db.get(VTModel, data.value_type_id)
            if not vt:
                raise GraphQLError(f"ValueType {data.value_type_id} not found")
            model.value_type_id = data.value_type_id
        if data.code_name is not None:
            model.code_name = data.code_name
        if data.description is not None:
            model.description = data.description

        await ctx.db.commit()
        await ctx.db.refresh(model)
        return _payload_type_from_model(model)

    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def delete_payload_type(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> bool:
        await require_permissions(info, P.STATS_DELETE)
        ctx = info.context

        node = await id.resolve_node(info, ensure_type=PayloadTypeType)
        if not node:
            raise GraphQLError(f"PayloadType {id} not found")

        model = await ctx.db.get(PTModel, node.db_id)
        if model:
            await ctx.db.delete(model)
            await ctx.db.commit()
        return True

    # -------------------------------------------------------------------------
    # AllowedPayloadRule Mutations (составной ключ)
    # -------------------------------------------------------------------------
    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def create_allowed_payload_rule(
            self,
            info: Info,
            data: CreateAllowedPayloadRuleInput,
    ) -> AllowedPayloadRuleType:
        await require_permissions(info, P.STATS_CREATE)
        ctx = info.context

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
        )

    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def update_allowed_payload_rule(
            self,
            info: Info,
            id: relay.GlobalID,
            data: UpdateAllowedPayloadRuleInput,
    ) -> AllowedPayloadRuleType:
        await require_permissions(info, P.STATS_EDIT)
        ctx = info.context

        # Декодируем составной ключ из GlobalID
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

        # Проверка новых ссылок
        et = await ctx.db.get(ETModel, data.new_event_type_id)
        pt = await ctx.db.get(PTModel, data.new_payload_type_id)
        if not et or not pt:
            raise GraphQLError("Новый EventType или PayloadType не найден")

        # Проверка на конфликт
        conflict = await ctx.db.execute(
            select(APModel).where(
                APModel.event_type_id == data.new_event_type_id,
                APModel.payload_type_id == data.new_payload_type_id,
            )
        )
        if conflict.scalar_one_or_none():
            raise GraphQLError("Такое правило уже существует")

        # Удаляем старое, создаём новое (т.к. ключ составной)
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
        )

    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def delete_allowed_payload_rule(
            self,
            info: Info,
            id: relay.GlobalID,
    ) -> bool:
        await require_permissions(info, P.STATS_DELETE)
        ctx = info.context

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

    # -------------------------------------------------------------------------
    # Review Mutations
    # -------------------------------------------------------------------------
    @strawberry.mutation  # type: ignore[unresolved-reference]
    async def update_review(
            self,
            info: Info,
            id: relay.GlobalID,
            data: UpdateReviewInput,
    ) -> ReviewType:
        """
        Обновление существующего отзыва.

        ⚠️ Создание и удаление отзывов доступно только через публичный REST API.
        """
        await require_permissions(info, P.REVIEWS_EDIT)
        ctx = info.context

        node = await id.resolve_node(info, ensure_type=ReviewType)
        if not node:
            raise GraphQLError(f"Review {id} not found")

        model = await ctx.db.get(ReviewModel, node.db_id)
        if not model:
            raise GraphQLError(f"Review {node.db_id} not found in DB")

        if data.problem_id is not None:
            model.problem_id = data.problem_id
        if data.status_id is not None:
            model.review_status_id = data.status_id
        if data.text is not None:
            model.text = data.text
        if data.image_name is not None:
            model.image_name = data.image_name

        await ctx.db.commit()
        await ctx.db.refresh(model)
        return _review_from_model(model)
