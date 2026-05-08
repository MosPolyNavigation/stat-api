import strawberry
from strawberry.extensions import QueryDepthLimiter
from .event_mutation import EventDictionaryMutation
from .mutation import Mutation
from .query import Query
from .logging import build_graphql_error_log


class StatAPISchema(strawberry.Schema):
    def process_errors(self, errors, execution_context=None) -> None:
        if execution_context is None or execution_context.context is None:
            return None

        context = execution_context.context
        request = context.get("request")

        for error in errors:
            field_name = None
            if getattr(error, "path", None):
                field_name = str(error.path[0])

            text = build_graphql_error_log(field_name, error)
            if text and request is not None:
                request.state.graphql_error_logs.append(text)

            original_error = getattr(error, "original_error", None)
            if original_error is not None and hasattr(original_error, "__traceback__"):
                original_error.__traceback__ = None

        return None


schema = StatAPISchema(
    query=Query,
    mutation=Mutation,
    extensions=[QueryDepthLimiter(max_depth=4)],
)
