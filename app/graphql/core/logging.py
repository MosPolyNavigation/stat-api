from graphql import GraphQLError
import strawberry
from strawberry.extensions import FieldExtension


GRAPHQL_EXCLUDED_FIELDS = {
    "event",
    "events",
    "payload",
    "payloads",
    "endpoint_statistics",
    "endpoint_statistics_avg",
}


def should_skip_graphql_logging(field_name: str) -> bool:
    if field_name in GRAPHQL_EXCLUDED_FIELDS:
        return True

    if "tg" in field_name.lower() or "dod" in field_name.lower():
        return True

    return False


def _extract_updated_fields(data) -> list[str]:
    fields = []
    if data is None:
        return fields

    for field_name in getattr(data, "__dict__", {}):
        if field_name.startswith("_"):
            continue
        if getattr(data, field_name) is not None:
            fields.append(field_name)

    return fields


def _extract_role_rights(role) -> list[str]:
    rights = []
    role_right_goals = getattr(role, "role_right_goals", None) or []
    for role_right_goal in role_right_goals:
        right = getattr(role_right_goal, "right", None)
        goal = getattr(role_right_goal, "goal", None)
        if right is not None and goal is not None:
            rights.append(f"{right.name} -> {goal.name}")  # noqa
            continue

        right_id = getattr(role_right_goal, "right_id", None)
        goal_id = getattr(role_right_goal, "goal_id", None)
        rights.append(f"{right_id} -> {goal_id}")

    return rights


def build_graphql_success_log(field_name: str, kwargs: dict, result) -> str | None:
    if should_skip_graphql_logging(field_name):
        return None

    if field_name in {
        "create_user",
        "update_user",
        "delete_user",
        "change_user_password",
        "create_role",
        "update_role",
        "delete_role",
        "grant_role",
        "revoke_role"
    }:
        return None

    operation = field_name.lower()

    if operation.startswith("create"):
        record_id = getattr(result, "id", None)
        if record_id is not None:
            return f"Создана запись (ID: {record_id})"
        return "Создана запись"

    if operation.startswith("update"):
        fields = _extract_updated_fields(kwargs.get("data"))
        return f"Обновлены поля: {fields}"

    if operation.startswith("delete"):
        deleted_id = getattr(result, "deleted_id", None)
        if deleted_id is not None:
            return f"Удалены записи (IDs: [{deleted_id}])"
        return "Удалены записи"

    return f"Выполнено действие просмотра {field_name}"


def build_graphql_error_log(field_name: str | None, error: GraphQLError) -> str | None:
    if field_name is not None and should_skip_graphql_logging(field_name):
        return None

    error_message = str(error)
    lowered = error_message.lower()

    if any(token in lowered for token in ["недостаточно прав", "not authorized", "forbidden", "unauthorized"]):
        if field_name == "create_role" or field_name == "update_role" or field_name == "grant_role":
            return "Попытка повысить привилегии"
        if field_name == "revoke_role":
            return "Попытка отозвать роль с большими правами"
        if field_name == "delete_role":
            return "Попытка удалить роль с большими правами"
        return "Попытка выполнить действие за рамками прав пользователя"

    original_error = getattr(error, "original_error", None)
    error_type = type(original_error).__name__ if original_error is not None else type(error).__name__
    return f"GraphQL-запрос завершился с ошибкой: {error_type}"


GRAPHQL_PERMISSION_ERROR_TOKENS = (
    "недостаточно прав",
    "forbidden",
    "unauthorized",
    "not authorized",
)


def is_graphql_permission_error_message(message: str) -> bool:
    lowered = message.lower()
    return any(token in lowered for token in GRAPHQL_PERMISSION_ERROR_TOKENS)


def build_public_graphql_error_message(message: str) -> str:
    if is_graphql_permission_error_message(message):
        return "Недостаточно прав для выполнения операции"

    return message


class GraphQLLoggingExtension(FieldExtension):
    async def resolve_async(self, next_, source, info: strawberry.Info, **kwargs):
        result = await next_(source, info, **kwargs)

        field_name = info.python_name
        if should_skip_graphql_logging(field_name):
            return result

        logger = getattr(info.context, "user_logger", None)
        current_user = getattr(info.context, "current_user", None)
        if logger is None or current_user is None:
            return result

        text = build_graphql_success_log(field_name, kwargs, result)
        if text:
            logger.log(current_user, text)  # type: ignore

        return result


def graphql_field(*args, **kwargs):
    extensions = list(kwargs.pop("extensions", []))
    extensions.append(GraphQLLoggingExtension())
    kwargs["extensions"] = extensions
    return strawberry.field(*args, **kwargs)


def graphql_mutation(*args, **kwargs):
    extensions = list(kwargs.pop("extensions", []))
    extensions.append(GraphQLLoggingExtension())
    kwargs["extensions"] = extensions
    return strawberry.mutation(*args, **kwargs)
