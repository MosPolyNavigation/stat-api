from strawberry import Schema
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import QueryDepthLimiter

from app.graphql.core.schema import StatAPISchema
from app.graphql.core.router import StatAPIGraphQLRouter, get_context

from .query import Query
from .mutation import Mutation

# Фабрика схемы
schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[QueryDepthLimiter(max_depth=10)],
)

# Экспорт роутера для FastAPI
graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide=None,
)
