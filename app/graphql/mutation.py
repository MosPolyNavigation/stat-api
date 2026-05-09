import strawberry
from app.graphql.domains.event_system.mutation import Mutation as EventMutation


@strawberry.type
class Mutation(EventMutation):  # ← добавлено
    pass
