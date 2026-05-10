import strawberry
from strawberry import Info
from sqlalchemy import select
from graphql import GraphQLError
from typing import List

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
    CreateAllowedPayloadRuleInput, UpdateAllowedPayloadRuleInput, DashboardTypeInput,
)
from app.graphql.domains.event_system.types import (
    AllowedPayloadRule as AllowedPayloadRuleType,
    Dashboard as DashboardType,
    _dashboard_from_model
)
from app.models import (
    EventType as ETModel,
    PayloadType as PTModel,
    AllowedPayload as APModel,
    DashboardType as DTModel,
    Dashboard as DashboardModel,
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
            event_type_id: int,
            payload_type_id: int,
            data: UpdateAllowedPayloadRuleInput,
    ) -> AllowedPayloadRuleType:
        await require_permissions(info, P.STATS_EDIT)
        ctx: GraphQLContext = info.context

        old_event_id, old_payload_id = event_type_id, payload_type_id

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
            event_type_id: int,
            payload_type_id: int
    ) -> bool:
        await require_permissions(info, P.STATS_DELETE)
        ctx: GraphQLContext = info.context

        rule = await ctx.db.execute(
            select(APModel).where(
                APModel.event_type_id == event_type_id,
                APModel.payload_type_id == payload_type_id,
            )
        )
        rule_model = rule.scalar_one_or_none()
        if not rule_model:
            raise GraphQLError("Правило не найдено")

        await ctx.db.delete(rule_model)
        await ctx.db.commit()
        return True


# =============================================================================
# Dashboard Mutations (Кастомные, без ResourceConfig)
# =============================================================================
@strawberry.type
class DashboardMutation:
    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])  # type: ignore
    async def create_dashboard(
            self,
            info: Info,
            data: DashboardTypeInput,
    ) -> DashboardType:
        await require_permissions(info, P.DASHBOARDS_CREATE)
        ctx: GraphQLContext = info.context

        # Валидация
        if data.display_order < 0:
            raise GraphQLError("display_order >= 0")
        if not data.title_text.strip():
            raise GraphQLError("title_text не может быть пустым")

        # Проверка FK
        if not await ctx.db.get(ETModel, data.event_type_id):
            raise GraphQLError(f"EventType {data.event_type_id} не найден")
        if not await ctx.db.get(DTModel, data.dashboard_type_id):
            raise GraphQLError(f"DashboardType {data.dashboard_type_id} не найден")

        model = DashboardModel(
            display_order=data.display_order, event_type_id=data.event_type_id,
            dashboard_type_id=data.dashboard_type_id, title_text=data.title_text.strip()
        )
        ctx.db.add(model)
        await ctx.db.commit()
        await ctx.db.refresh(model)
        return _dashboard_from_model(model)

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])  # type: ignore
    async def create_dashboards(
            self,
            info: Info,
            inputs: List[DashboardTypeInput],
    ) -> List[DashboardType]:
        await require_permissions(info, P.DASHBOARDS_CREATE)
        ctx: GraphQLContext = info.context
        if not inputs:
            raise GraphQLError("inputs не может быть пустым")

        for i, inp in enumerate(inputs):
            if inp.display_order < 0:
                raise GraphQLError(f"[{i}] display_order >= 0")
            if not inp.title_text.strip():
                raise GraphQLError(f"[{i}] title_text не пустой")

        # Bulk FK check
        for et_id in {i.event_type_id for i in inputs}:
            if not await ctx.db.get(ETModel, et_id):
                raise GraphQLError(f"EventType {et_id} не найден")
        for dt_id in {i.dashboard_type_id for i in inputs}:
            if not await ctx.db.get(DTModel, dt_id):
                raise GraphQLError(f"DashboardType {dt_id} не найден")

        models = [DashboardModel(
            display_order=i.display_order,
            event_type_id=i.event_type_id,
            dashboard_type_id=i.dashboard_type_id,
            title_text=i.title_text.strip()
        ) for i in inputs]
        ctx.db.add_all(models)
        await ctx.db.commit()
        return [_dashboard_from_model(m) for m in models]

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])  # type: ignore
    async def update_dashboard(
            self, info: Info, id: int, data: DashboardTypeInput
    ) -> DashboardType:
        await require_permissions(info, P.DASHBOARDS_EDIT)
        ctx: GraphQLContext = info.context

        if data.display_order < 0:
            raise GraphQLError("display_order >= 0")
        if not data.title_text.strip():
            raise GraphQLError("title_text не пустой")
        if not await ctx.db.get(ETModel, data.event_type_id):
            raise GraphQLError(f"EventType {data.event_type_id} не найден")
        if not await ctx.db.get(DTModel, data.dashboard_type_id):
            raise GraphQLError(f"DashboardType {data.dashboard_type_id} не найден")

        model = await ctx.db.get(DashboardModel, id)
        if not model:
            raise GraphQLError(f"Dashboard {id} не найден")

        model.display_order = data.display_order
        model.event_type_id = data.event_type_id
        model.dashboard_type_id = data.dashboard_type_id
        model.title_text = data.title_text.strip()
        await ctx.db.commit()
        await ctx.db.refresh(model)
        return _dashboard_from_model(model)  # type: ignore[arg-type]

    @strawberry.mutation(extensions=[GraphQLLoggingExtension()])  # type: ignore
    async def delete_dashboard(self, info: Info, id: int) -> bool:
        await require_permissions(info, P.DASHBOARDS_DELETE)
        ctx: GraphQLContext = info.context
        model = await ctx.db.get(DashboardModel, id)
        if not model:
            raise GraphQLError(f"Dashboard {id} не найден")
        await ctx.db.delete(model)
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
    DashboardMutation,
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
       - create/update/delete_dashboard
    """
    pass
