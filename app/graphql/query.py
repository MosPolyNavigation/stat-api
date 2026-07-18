import strawberry

from app.graphql.domains.event_system.query import Query as EventQuery
from app.graphql.domains.navigation.query import Query as NavQuery
from app.graphql.domains.auth.query import Query as AuthQuery
from app.graphql.domains.stat.query import Query as StatsQuery


@strawberry.type
class Query(EventQuery, NavQuery, AuthQuery, StatsQuery):
    pass
