from typing import Type, Optional, Any, cast, Iterable
import re
import strawberry
from strawberry import relay, Info
from sqlalchemy import select
from graphql import GraphQLError

from .resource import ResourceConfig
from .permissions import require_permissions
from .filters import apply_filters
from .ordering import apply_order_by
from .pagination import fetch_relay_page
from .context import GraphQLContext
from .logging import GraphQLLoggingExtension, should_skip_graphql_logging


def _make_base_name(name: str) -> str:
    """Превращает 'EventType' или 'ReviewModel' в 'event_type'."""
    base = name.removesuffix("Type").removesuffix("Model")
    return re.sub(r'(?<!^)(?=[A-Z])', '_', base).lower()


# =============================================================================
# Фабрика Query
# =============================================================================
def create_query_resource(
        config: ResourceConfig,
        *,
        enable_list: bool = True,
        enable_get: bool = True,
        name_list: Optional[str] = None,
        name_get: Optional[str] = None,
) -> Type[Any]:
    """Создаёт Strawberry-класс Query с настраиваемыми методами."""
    base_name = _make_base_name(config.graphql_type.__name__)
    list_name = name_list or f"{base_name}s"
    get_name = name_get or base_name
    attrs: dict[str, Any] = {"config": config}

    if enable_list:
        async def _list_resolver(self, info, first=None, after=None, filter=None, order_by=None):
            if config.permissions.view:
                await require_permissions(info, config.permissions.view)
            ctx: GraphQLContext = info.context
            stmt = select(config.model)
            if filter:
                stmt = apply_filters(stmt, config.model, filter)

            if order_by is not None and config.order_by_input:
                stmt = apply_order_by(stmt, config.model, order_by)
            elif config.order_by is not None:
                stmt = stmt.order_by(config.order_by)
            else:
                stmt = stmt.order_by(getattr(config.model, "id").asc())
            return await fetch_relay_page(
                session=ctx.db, stmt=stmt, first=first, after=after,
                model=config.model, cursor_fields=config.cursor_field,
                cursor_separator=config.cursor_separator, convert=config.convert,
            )

        _node_type = cast(type, config.graphql_type)
        _list_resolver.__annotations__ = {
            "info": Info,
            "first": Optional[int],
            "after": Optional[str],
            "filter": Optional[config.filter_input],  # type: ignore
            "order_by": Optional[config.order_by_input],  # type: ignore
            "return": Iterable[_node_type],  # type: ignore
        }

        # 🔹 Логирование: проверяем флаги + глобальные исключения
        extensions = []
        if config.should_log("list") and not should_skip_graphql_logging(list_name):
            extensions.append(GraphQLLoggingExtension())

        connection_type = relay.ListConnection.__class_getitem__(_node_type)  # noqa
        _list_resolver = relay.connection(connection_type, extensions=extensions)(_list_resolver)
        _list_resolver.__name__ = list_name
        attrs[list_name] = _list_resolver

    if enable_get:
        async def _get_resolver(self, info, id):
            if config.permissions.view:
                await require_permissions(info, config.permissions.view)
            return await id.resolve_node(info, ensure_type=config.graphql_type)

        _get_resolver.__annotations__ = {
            "info": Info,
            "id": relay.GlobalID,
            "return": Optional[config.graphql_type],  # type: ignore
        }
        
        # 🔹 Логирование для одиночного запроса
        extensions = []
        if config.should_log("get") and not should_skip_graphql_logging(get_name):
            extensions.append(GraphQLLoggingExtension())
        
        _get_resolver = strawberry.field(extensions=extensions)(_get_resolver)
        _get_resolver.__name__ = get_name
        attrs[get_name] = _get_resolver

    return strawberry.type(type(f"{base_name.title()}Query", (object,), attrs))


# =============================================================================
# Фабрика Mutation
# =============================================================================
def create_mutation_resource(
    config: ResourceConfig,
    *,
    enable_create: bool = True,
    enable_update: bool = True,
    enable_delete: bool = True,
    name_create: Optional[str] = None,
    name_update: Optional[str] = None,
    name_delete: Optional[str] = None,
    create_input: Optional[Type] = None,
    update_input: Optional[Type] = None,
) -> Type[Any]:
    """Создаёт Strawberry-класс Mutation с настраиваемыми операциями."""
    base_name = _make_base_name(config.graphql_type.__name__)
    create_name = name_create or f"create_{base_name}"
    update_name = name_update or f"update_{base_name}"
    delete_name = name_delete or f"delete_{base_name}"
    attrs: dict[str, Any] = {"config": config}

    # --- CREATE ---
    if enable_create and create_input:
        async def _create_resolver(self, info, data):
            if config.permissions.create:
                await require_permissions(info, config.permissions.create)
            ctx: GraphQLContext = info.context
            for field_name, validator in config.validators.items():
                val = getattr(data, field_name, None)
                if val is not None:
                    res = validator(val)
                    if res is not True and isinstance(res, str):
                        raise GraphQLError(f"{field_name}: {res}")
            instance = config.model(**{
                k: v for k, v in data.__dict__.items()
                if k in {c.name for c in config.model.__table__.columns} and v is not None
            })
            ctx.db.add(instance)
            await ctx.db.commit()
            await ctx.db.refresh(instance)
            return config.convert(instance)

        _create_resolver.__annotations__ = {
            "info": Info,
            "data": create_input,  # type: ignore
            "return": config.graphql_type,  # type: ignore
        }

        # 🔹 Логирование для create
        extensions = []
        if config.should_log("create") and not should_skip_graphql_logging(create_name):
            extensions.append(GraphQLLoggingExtension())

        _create_resolver = strawberry.mutation(extensions=extensions)(_create_resolver)
        _create_resolver.__name__ = create_name
        attrs[create_name] = _create_resolver

    # --- UPDATE ---
    if enable_update and update_input:
        async def _update_resolver(self, info, id, data):
            if config.permissions.edit:
                await require_permissions(info, config.permissions.edit)
            ctx: GraphQLContext = info.context
            node = await id.resolve_node(info, ensure_type=config.graphql_type)
            if not node:
                raise GraphQLError(f"{config.graphql_type.__name__} {id} not found")
            model = await ctx.db.get(config.model, node.db_id)
            if not model:
                raise GraphQLError(f"{config.model.__name__} {node.db_id} not found in DB")
            for field_name, validator in config.validators.items():
                val = getattr(data, field_name, None)
                if val is not None:
                    res = validator(val)
                    if res is not True and isinstance(res, str):
                        raise GraphQLError(f"{field_name}: {res}")
            for k, v in data.__dict__.items():
                if v is not None and hasattr(model, k):
                    setattr(model, k, v)
            await ctx.db.commit()
            await ctx.db.refresh(model)
            return config.convert(model)

        _update_resolver.__annotations__ = {
            "info": Info,
            "id": relay.GlobalID,
            "data": update_input,
            "return": config.graphql_type,
        }

        # 🔹 Логирование для update
        extensions = []
        if config.should_log("update") and not should_skip_graphql_logging(update_name):
            extensions.append(GraphQLLoggingExtension())

        _update_resolver = strawberry.mutation(extensions=extensions)(_update_resolver)
        _update_resolver.__name__ = update_name
        attrs[update_name] = _update_resolver

    # --- DELETE ---
    if enable_delete:
        async def _delete_resolver(self, info, id):
            if config.permissions.delete:
                await require_permissions(info, config.permissions.delete)
            ctx: GraphQLContext = info.context
            node = await id.resolve_node(info, ensure_type=config.graphql_type)
            if not node:
                raise GraphQLError(f"{config.graphql_type.__name__} {id} not found")
            model = await ctx.db.get(config.model, node.db_id)
            if model:
                await ctx.db.delete(model)
                await ctx.db.commit()
            return True

        _delete_resolver.__annotations__ = {
            "info": Info,
            "id": relay.GlobalID,
            "return": bool,
        }

        # 🔹 Логирование для delete
        extensions = []
        if config.should_log("delete") and not should_skip_graphql_logging(delete_name):
            extensions.append(GraphQLLoggingExtension())

        _delete_resolver = strawberry.mutation(extensions=extensions)(_delete_resolver)
        _delete_resolver.__name__ = delete_name
        attrs[delete_name] = _delete_resolver

    return strawberry.type(type(f"{base_name.title()}Mutation", (object,), attrs))
