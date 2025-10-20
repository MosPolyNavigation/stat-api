from fastapi import Depends
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from app.database import get_db
from app.routes.graphql.schema import schema


async def get_context(
    db: Session = Depends(get_db)
) -> dict[str, Session]:
    return {"db": db}

graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context
)
