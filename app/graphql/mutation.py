import strawberry
from app.graphql.domains.event_system.mutation import Mutation as EventMutation
from app.graphql.domains.navigation.mutation import Mutation as NavMutation


@strawberry.type
class Mutation(
    EventMutation,
    NavMutation
):
    pass
