import strawberry
from strawberry import relay

from app.graphql.domains.event_system.query import Query as EventQuery


@strawberry.type
class Query(EventQuery):
    node: relay.Node = relay.node()
