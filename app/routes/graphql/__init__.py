from typing import Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

from app.database import get_db
from app.helpers.auth_utils import get_current_active_user
from app.models import User
from app.routes.graphql.logging import (
    build_public_graphql_error_message,
    is_graphql_permission_error_message,
)
from app.routes.graphql.schema import schema
from app.services.permission_service import PermissionService
from app.services.user_logger_service import UserLoggerService


async def get_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    user_logger = UserLoggerService(db)

    request.state.current_user = current_user
    request.state.user_logger = user_logger
    request.state.graphql_error_logs = []

    return {
        "db": db,
        "current_user": current_user,
        "permission_service": PermissionService(db),
        "user_logger": user_logger,
        "request": request,
    }


class StatAPIGraphQLRouter(GraphQLRouter):
    async def process_result(
        self,
        request: Request,
        result: ExecutionResult,
    ) -> GraphQLHTTPResponse:
        logger = getattr(request.state, "user_logger", None)
        current_user = getattr(request.state, "current_user", None)
        error_logs = getattr(request.state, "graphql_error_logs", [])

        if logger is not None and current_user is not None:
            for text in error_logs:
                logger.log(current_user, text)

        response: GraphQLHTTPResponse = {"data": result.data}

        if result.errors:
            formatted_errors = []
            for error in result.errors:
                formatted = dict(error.formatted)
                original_message = formatted.get("message", "")
                public_message = build_public_graphql_error_message(original_message)

                formatted["message"] = public_message

                if is_graphql_permission_error_message(original_message):
                    formatted.pop("extensions", None)

                formatted_errors.append(formatted)

            response["errors"] = formatted_errors

        return response


graphql_router = StatAPIGraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide=None,
)