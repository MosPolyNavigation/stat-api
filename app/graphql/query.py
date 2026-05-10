import strawberry

from app.graphql.domains.event_system.query import Query as EventQuery
from app.graphql.domains.navigation.query import Query as NavQuery


@strawberry.type
class Query(
    EventQuery,
    NavQuery
):
    pass
