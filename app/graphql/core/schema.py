from typing import Optional, List, Union

import strawberry
from strawberry.types import ExecutionContext
from app.graphql.core.logging import build_graphql_error_log


class StatAPISchema(strawberry.Schema):
    def process_errors(
        self, errors, execution_context: ExecutionContext | None = None
    ) -> None:
        if execution_context is None or execution_context.context is None:
            return

        ctx = execution_context.context
        request = ctx.request

        for error in errors:
            # Безопасное получение пути
            path: Optional[List[Union[str, int]]] = getattr(error, "path", None)
            field_name = str(path[0]) if path else None

            text = build_graphql_error_log(field_name, error)
            if text:
                ctx.error_logs.append(text)
                # Дублируем в request.state для совместимости с router
                if not hasattr(request.state, "graphql_error_logs"):
                    request.state.graphql_error_logs = []
                request.state.graphql_error_logs.append(text)

            # Очистка traceback для предотвращения утечек памяти
            original_error = getattr(error, "original_error", None)
            if original_error is not None and hasattr(original_error, "__traceback__"):
                original_error.__traceback__ = None
