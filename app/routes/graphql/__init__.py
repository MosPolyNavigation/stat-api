from typing import Any
from fastapi import Depends
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from app.database import get_db
from app.helpers.auth_utils import get_current_active_user
from app.models import User
from app.routes.graphql.schema import schema


async def get_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    return {
        "db": db,
        "current_user": current_user
    }

graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context
)
