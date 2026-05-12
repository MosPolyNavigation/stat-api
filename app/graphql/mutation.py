import strawberry
from app.graphql.domains.event_system.mutation import Mutation as EventMutation
from app.graphql.domains.navigation.mutation import Mutation as NavMutation
from app.graphql.domains.auth.mutation import Mutation as AuthMutation


@strawberry.type
class Mutation(
    EventMutation,
    NavMutation,
    AuthMutation,
):
    pass
